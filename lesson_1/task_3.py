"""
Задание 3.

Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b'' (без encode decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- обязательно!!! усложните задачу, "отловив" и обработав исключение,
придумайте как это сделать
"""

word_list = ['attribute', 'класс', 'функция', 'type']
success_list = []
cant_use_ascii = []

for word in word_list:
    try:
        byte_str = bytes(word, 'ascii')
        success_list.append(word)
    except UnicodeEncodeError:
        cant_use_ascii.append(word)
        print(f'Не удалось преобразовать слово "{word}" с помощью маркировки b"", '
              f'слово добавлено в соответствующий список исключений')

print('Преобразованы следующие элементы:')
for el in success_list:
    print(el)
print('Не удалось преобразовать следующие элементы:')
for el in cant_use_ascii:
    print(el)
