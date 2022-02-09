"""Программа-сервер"""

import sys
import time
import argparse
import select
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, ERROR, DEFAULT_PORT, MESSAGE, \
    MESSAGE_TEXT, SENDER, TIME, USER, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from common.utils import get_message, send_message
from logs import server_log_config
from decorator import log

logs = getLogger('server')


@log
def process_client_message(message, messages_list, client, clients, names):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    проверяет корректность, отправляет словарь-ответ в случае необходимости.
    :param message:
    :param messages_list:
    :param client:
    :param clients:
    :param names:
    :return:
    """
    logs.debug(f'Разбор сообщения от клиента : {message}')

    # Если это сообщение о присутствии, принимаем и отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and \
            TIME in message and USER in message:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, иначе отправляем ответ и завершаем соединение.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если это сообщение, то добавляем его в очередь сообщений.
    # Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    # Если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Иначе отдаём Bad request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        logs.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        logs.error(f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        logs.critical(f'Попытка запуска сервера с указанием неподходящего порта {listen_port}. '
                      f'Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    """
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8079 -a 127.0.0.1
    :return:
    """
    listen_address, listen_port = arg_parser()
    logs.info(f'Запущен сервер, порт для подключений: {listen_port}, адрес с которого принимаются подключения: '
              f'{listen_address}.')
    # Готовим сокет, выставляем таймаут и создаем списки клиентов и сообщений
    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
    clients_lst = []
    messages_lst = []
    names = dict()
    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)
    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            logs.info(f'Установлено соединение с {client_address}')
            clients_lst.append(client)
        # создаем переменные для принятия данных от select
        recv_lst = []
        send_lst = []
        err_lst = []
        try:
            if clients_lst:
                # recv_lst-список клиентов, отправивших сообщение,send_lst- список клиентов,ждущих сообщение
                recv_lst, send_lst, err_lst = select.select(clients_lst, clients_lst, [], 0)
        except OSError:
            pass
        if recv_lst:
            for client_with_messages in recv_lst:
                try:
                    process_client_message(get_message(client_with_messages), messages_lst, client_with_messages,
                                           clients_lst, names)
                except:
                    logs.info(f'Клиент {client_with_messages.getpeername()} отключился от сервера.')
                    clients_lst.remove(client_with_messages)

        for i in messages_lst:
            try:
                process_message(i, names, send_lst)
            except Exception:
                logs.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients_lst.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages_lst.clear()


if __name__ == '__main__':
    main()
