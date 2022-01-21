"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""
original_list = ['разработка', 'администрирование', 'protocol', 'standard']
decoded_list = []
encoded_list = []

print(original_list)

for el in original_list:
    encoded_el = el.encode('utf-8')
    encoded_list.append(encoded_el)

print(encoded_list)

for el in encoded_list:
    decoded_el = el.decode('utf-8')
    decoded_list.append(decoded_el)

print(decoded_list)
