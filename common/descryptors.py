import logging
import sys

if sys.argv[0].find('client') == -1:
    logs = logging.getLogger('server')
else:
    logs = logging.getLogger('client')


# Дескриптор для описания порта:
class Port:
    """
    Класс - дескриптор для номера порта.
    Позволяет использовать только порты с 1023 по 65536.
    При попытке установить неподходящий номер порта генерирует исключение.
    """

    def __set__(self, instance, value):
        # instance - <__main__.Server object at 0x000000D582740C50>
        # value - 7780
        if not 1023 < value < 65536:
            logs.critical(f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с 1024 '
                          f'до 65535.')
            exit(1)
        # Если порт прошел проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        # owner - <class '__main__.Server'>
        # name - port
        self.name = name
