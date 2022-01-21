"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""

import re
import csv
from chardet import detect


def get_data():
    vendor_list = list()
    os_name_list = list()
    product_code_list = list()
    product_type_list = list()
    main_data = list()

    for i in range(1, 4):
        with open(f'info_{i}.txt', 'rb') as file:
            text = file.read()
        encoding = detect(text)['encoding']
        print(encoding)
        file_obj = open(f'info_{i}.txt', encoding=encoding)
        data = file_obj.read()

        vendor = re.compile(r'Изготовитель системы:\s*\S*')
        vendor_list.append(vendor.findall(data)[0].split()[2])

        os_name = re.compile(r'Windows\s\S*')
        os_name_list.append(os_name.findall(data)[0])

        product_code = re.compile(r'Код продукта:\s*\S*')
        product_code_list.append(product_code.findall(data)[0].split()[2])

        product_type = re.compile(r'Тип системы:\s*\S*')
        product_type_list.append(product_type.findall(data)[0].split()[2])

    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)

    for i in range(0, 3):
        row_data = [i + 1, vendor_list[i], os_name_list[i], product_code_list[i], product_type_list[i]]
        main_data.append(row_data)
    return main_data


def write_to_csv(file):
    main_data = get_data()
    with open(file, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in main_data:
            writer.writerow(row)


write_to_csv('new_data.csv')
