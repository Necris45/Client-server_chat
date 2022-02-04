"""Программа-клиент"""

import sys
import json
import time
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message
from logs import client_log_config
from decorator import log

logs = getLogger('client')


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
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            logs.info('Подключение успешно')
            return '200 : OK'
        logs.error('Клиент не подключился к серверу')
        return f'400 : {message[ERROR]}'
    logs.error('Некоректный ответ от сервера при попытке подключения')
    raise ValueError


def main():
    """Загружаем параметы коммандной строки"""
    # client.py 127.0.0.1 8079
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
        logs.warning(f"Параметры IP-адреса и порта не переданы и установлены по умолчанию: IP - {server_address}, "
                     f"PORT - {server_port}")
    except ValueError:
        logs.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Инициализация сокета и обмен
    exchanger = socket(AF_INET, SOCK_STREAM)
    try:
        exchanger.connect((server_address, server_port))
    except ConnectionRefusedError:
        logs.critical('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
        sys.exit(1)
    message_to_server = create_presence()
    send_message(exchanger, message_to_server)
    try:
        answer = process_ans(get_message(exchanger))
        logs.debug(answer)
    except (ValueError, json.JSONDecodeError):
        logs.error('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
