import socket

def main():

    # Создаем объект сокета
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Устанавливаем соединение
    server_address = ('localhost', 6000)
    client_socket.connect(server_address)
    client_socket.send(input("Enter a number: ").encode())
    try:
        while True:
            # Получаем ответ от сервера
            data = client_socket.recv(1024)
            print('Received:', data.decode())
    finally:
        # Закрываем соединение
        client_socket.close()


if __name__ == '__main__':

    main()

    c = C(1, 2, 6)
    print(c)
