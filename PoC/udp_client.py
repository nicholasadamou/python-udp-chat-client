import socket
import threading


class Client:
    BUFFER_SIZE = 4096
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    NEW_CLIENT_MESSAGE = '{NEW CLIENT REQUEST}'
    QUIT_MESSAGE = '{QUIT}'
    NICKNAME_ALREADY_EXISTS_MESSAGE = '{NICKNAME ALREADY EXISTS}'

    def __init__(self, address, port):
        self.addr = address
        self.port = port

        self.client = (self.addr, self.port)

        self.nickname = self.obtain_nickname(self.client)

        threading.Thread(target=self.receive_message, args=(self.client_socket,)).start()

        self.send_message()

    def obtain_nickname(self, client):
        while 1:
            print('[!] Please enter your nickname: ')
            nickname = input('> ')
            payload = Client.encode(nickname, self.NEW_CLIENT_MESSAGE)
            self.client_socket.sendto(payload, client)

            message, server_addr = self.client_socket.recvfrom(self.BUFFER_SIZE)

            message = message.decode('utf-8')

            if message == self.NICKNAME_ALREADY_EXISTS_MESSAGE:
                print("[!] ('%s'): is already taken." % nickname)
                continue
            else:
                break

        return nickname

    def send_message(self):
        while 1:
            message = input('%s > ' % self.nickname)

            payload = Client.encode(self.nickname, message)

            try:
                self.client_socket.sendto(payload, self.client)
            except socket.error:
                pass

            if message.lower() == self.QUIT_MESSAGE.lower():
                self.client_socket.close()

                break

    @staticmethod
    def encode(nickname, message):
        """Encodes a message as a comma separated list to be sent to the chat server"""

        # Construct the payload
        payload = '%s,%s' % (nickname, message)

        # Encode the payload as utf-8 byte stream, so it can be sent to the chat server
        return str.encode(payload, 'utf-8')

    def receive_message(self, client_socket):
        while 1:
            try:
                message, server_addr = client_socket.recvfrom(self.BUFFER_SIZE)

                if message:
                    message = message.decode('utf-8')

                    if message.lower() != self.NICKNAME_ALREADY_EXISTS_MESSAGE.lower():
                        print('%s' % message)
            except socket.error:
                break


if __name__ == '__main__':
    Client('127.0.0.1', 4096)
