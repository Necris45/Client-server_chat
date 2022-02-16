# Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
# Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
# В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
# («Узел доступен», «Узел недоступен»).
# При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
import socket
from ipaddress import ip_address
from subprocess import Popen, PIPE


def host_ping(lst_ip_address, timeout=500, requests=1):
    results = {'Доступные узлы': [], 'Недоступные узлы': []}
    for address in lst_ip_address:
        try:
            address = ip_address(address)
        except ValueError:
            address_exc = socket.gethostbyname(address)
            address = ip_address(address_exc)
        process = Popen(f'ping {address} -w {timeout} -n {requests}', stdout=PIPE)
        process.wait()
        if process.returncode == 0:
            results['Доступные узлы'].append(address)
            print('Узел доступен')
        else:
            results['Недоступные узлы'].append(address)
            print('Узел недоступен')
    return results


if __name__ == '__main__':
    lst_network_node = ['192.168.1.5', '192.168.1.1', '10.168.1.1', 'mail.ru']
    print(host_ping(lst_network_node))
