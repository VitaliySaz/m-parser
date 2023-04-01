import socket

import json

st = {
    'pars': [
        {'page_count': 10, 'category_id': 3}
    ],
}


def main():

    # Создаем объект сокета
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Устанавливаем соединение
    server_address = ('localhost', 6060)
    client_socket.connect(server_address)
    client_socket.send(json.dumps(st).encode())
    try:
        while True:
            # Получаем ответ от сервера
            data = client_socket.recv(1024)
            if data:
                print('Received:', data.decode())
    finally:
        # Закрываем соединение
        client_socket.close()


if __name__ == '__main__':
    main()
