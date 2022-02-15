# Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только последний
# октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
from subprocess import Popen, PIPE
from task_1 import host_ping
from ipaddress import ip_address

def host_range_ping():
    while True:
        start_ip = input('Введите первоначальный адрес')
        try:
            last_oct = int(start_ip.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        quantity = input('Введите кол-во адресов')
        try:
            quantity = int(quantity)
            break
        except Exception as e:
            print(e)
    new_ip_lst = []
    added_ip = ip_address(start_ip)
    if last_oct + quantity > 255:
        print(f'будет выведено только {quantity - (last_oct + quantity - 256)} адресов, так как остальные в диапазоне'
              f'имеют отличия не только в последнем октете')
    for i in range (0, quantity):
        new_ip = added_ip + i
        str_1 = str(new_ip)
        if str_1.split('.')[0:3] == start_ip.split('.')[0:3]:
            new_ip_lst.append(new_ip)
    result = host_ping(new_ip_lst)
    return result


if __name__ == '__main__':
    print(host_range_ping())
