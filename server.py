"""Программа-сервер"""

import sys
import time
import argparse
import select
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, ERROR, DEFAULT_PORT, MESSAGE, \
    MESSAGE_TEXT, SENDER, TIME, USER
from common.utils import get_message, send_message
from logs import server_log_config
from decorator import log

logs = getLogger('server')


@log
def process_client_message(message, messages_list, client):
    """
    Обработчик сообщений от клиентов, принимает словарь-сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message and \
            message[USER][ACCOUNT_NAME] == 'Guest':
        logs.info(f'Клиент {USER} подключился к серверу')
        send_message(client, {RESPONSE: 200})
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
    else:
        send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})
        logs.error('Клиент отправил некорректный запрос на подключение')


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
    logs.info(f'Запущен сервер, порт для подключений: {listen_port}, '
              f'адрес с которого принимаются подключения: {listen_address}. ')
    # Готовим сокет, выставляем таймаут и создаем списки клиентов и сообщений
    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
    clients_lst = []
    messages_lst = []
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
                    process_client_message(get_message(client_with_messages), messages_lst, client_with_messages)
                except:
                    logs.info(f'Клиент {client_with_messages.getpeername()} отключился от сервера.')
                    clients_lst.remove(client_with_messages)
        if messages_lst and send_lst:
            message = {ACTION: MESSAGE, SENDER: messages_lst[0][0],
                       TIME: time.time(), MESSAGE_TEXT: messages_lst[0][1]}
            del messages_lst[0]
            for expect_client in send_lst:
                try:
                    send_message(expect_client, message)
                except:
                    logs.info(f'Клиент {expect_client.getpeername()} отключился')
                    clients_lst.remove(expect_client)


if __name__ == '__main__':
    main()
