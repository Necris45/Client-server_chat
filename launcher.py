import subprocess
import time

PROCESSES = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, '
                   'x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESSES.append(subprocess.Popen('python server.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        time.sleep(1)
        PROCESSES.append(subprocess.Popen('python client.py -n test5',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        time.sleep(0.5)
        PROCESSES.append(subprocess.Popen('python client.py -n test10',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
