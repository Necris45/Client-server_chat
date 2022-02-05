"""Программа-клиент"""
import argparse
import json
import sys
import time
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, MESSAGE_TEXT, MESSAGE, SENDER
from common.utils import get_message, send_message
from errors import ServerError, ReqFieldMissingError
from logs import client_log_config
from decorator import log

logs = getLogger('client')


@log
def reciving_message_from_users(message):
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        logs.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        logs.error(f'От сервера получено некорректное сообщение : {message}')


@log
def create_message(sock, account_name='Guest'):
    message = input('Введите сообщение, для завершения работы введите - stop: ')
    if message == 'stop':
        sock.close()
        logs.info('Пользователь завершил работу')
        sys.exit(0)
    message_create = {ACTION: MESSAGE, TIME: time.time(), ACCOUNT_NAME: account_name,
                      MESSAGE_TEXT: message}
    logs.debug(f'Создано сообщение {message_create}')
    return message_create


@log
def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logs.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_ans(message):
    """
    Функция разбирает ответ сервера
    :param message:
    :return:
    """
    logs.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            logs.info('Подключение успешно')
            return '200 : OK'
        elif message[RESPONSE] == 400:
            logs.error('Клиент не подключился к серверу')
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        logs.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        logs.critical(f'Указан недопустимый режим работы {client_mode}, допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    """Загружаем параметы коммандной строки"""
    # client.py 127.0.0.1 8079
    server_address, server_port, client_mode = arg_parser()
    logs.info(f'Запущен клиент с ip-адресом{server_address}, порт:{server_port}, с режимом работы:{client_mode}')
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        answer = process_ans(get_message(transport))
        logs.info(f'Установлено соединение с сервером. Ответ от сервера {answer}')
    except json.JSONDecodeError:
        logs.error('Не удалось декодировать сообщение сервера.')
    except ConnectionRefusedError:
        logs.critical('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
        sys.exit(1)
    except ServerError:
        logs.error(f'При установке соединения сервер вернул ошибку: {ServerError}')
        sys.exit(1)
    except ValueError:
        logs.error('Не удалось декодировать сообщение сервера.')
    else:
        # Если соединение с сервером установлено корректно,
        # начинаем обмен с ним, согласно требуемому режиму.
        # основной цикл прогрммы:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            # режим работы - отправка сообщений
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logs.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            # Режим работы приём:
            if client_mode == 'listen':
                try:
                    reciving_message_from_users(get_message(transport))
                    print(get_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logs.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
