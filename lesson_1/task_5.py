"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""
import chardet
import subprocess

arg1 = ['ping', 'yandex.ru']
arg2 = ['ping', 'youtube.com']
arg_lst = [arg1, arg2]
for el in arg_lst:
    ping = subprocess.Popen(el, stdout=subprocess.PIPE)
    for line in ping.stdout:
        result = chardet.detect(line)
        print(result)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))
