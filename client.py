"""Программа-клиент"""
import argparse
import json
import sys
import time
import threading
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, MESSAGE_TEXT, MESSAGE, SENDER, EXIT, DESTINATION
from common.utils import get_message, send_message
from errors import ServerError, ReqFieldMissingError, IncorrectDataRecivedError
from logs import client_log_config
from decorator import log

logs = getLogger('client')


@log
def print_help():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def reciving_message_from_users(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                logs.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                            f'\n{message[MESSAGE_TEXT]}')
            else:
                logs.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            logs.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            logs.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def create_message(sock, account_name='Guest'):
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение, для завершения работы введите - stop: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    logs.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        logs.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        logs.critical('Потеряно соединение с сервером.')
        sys.exit(1)


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
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            logs.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        logs.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    """Сообщаем о запуске"""
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    logs.info(f'Запущен клиент с парамертами: адрес сервера: {server_address}, порт: {server_port}, '
              f'имя пользователя: {client_name}')
    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence(account_name=client_name)
        send_message(transport, message_to_server)
        answer = process_ans(get_message(transport))
        logs.info(f'Установлено соединение с сервером. Ответ от сервера {answer}')
    except json.JSONDecodeError:
        logs.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logs.critical('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
        sys.exit(1)
    except ServerError:
        logs.error(f'При установке соединения сервер вернул ошибку: {ServerError}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        logs.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ValueError:
        logs.error('Не удалось декодировать сообщение сервера.')
    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиенский процесс приёма сообщний
        receiver = threading.Thread(target=reciving_message_from_users, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()
        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        logs.debug('Запущены процессы')
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
