import socket


class Server:
    BUFFER_SIZE = 4096  # The size of the buffer to receive data from chat server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # The UDP server socket

    # Types of messages sent by the client
    NEW_CLIENT_MESSAGE = '{NEW CLIENT REQUEST}'  # Used to indicated a new client is connecting to the server
    QUIT_MESSAGE = '{QUIT}'  # Used to indicate a client is leaving the chat
    NICKNAME_ALREADY_EXISTS_MESSAGE = '{NICKNAME ALREADY EXISTS}'  # Used to indicate that the nickname already exists

    def __init__(self, address, port):
        # List of connected clients
        self.clients = {}

        self.addr = address  # The address of the server
        self.port = port  # The port of the server

        # Bind the server to this (address, port) tuple
        self.server_socket.bind((self.addr, self.port))

        # Acknowledge that the server is running and listening
        # for incoming connections
        print("[*] Waiting for Someone to Join the Chat")
        print("[*] Chat Server listening on ('%s', %s)" % (self.addr, self.port))

        # Accept and handle all incoming connections
        self.accept_incoming_connections(self.server_socket)

    def accept_incoming_connections(self, server_socket):
        """Handle all incoming connections"""

        # Store the current sequence #
        current_sequence_num = 0

        while 1:
            # Receive a message from the client
            data, address = server_socket.recvfrom(self.BUFFER_SIZE)

            # Decode the data sent by the client
            # and obtain the nickname and message sent by client
            nickname, message = Server.decode_message(data)

            # The address of the client
            addr = address[0]
            # The port used by the client
            port = address[1]

            # Check if the received message indicates that
            # a new client is connecting to the server
            if message.lower() == self.NEW_CLIENT_MESSAGE.lower():
                # Check if the client already exists
                if nickname not in self.clients:
                    # Add the client to the connected clients list
                    self.clients[nickname] = [address, current_sequence_num]

                    # Show that this client has connected
                    print("[+] 🖥️ Client (%s, '%s', %s): has connected" % (nickname, address[0], address[1]))

                    # Broadcast a message showing that this client has joined the chat
                    self.broadcast(server_socket, "%s has joined the chat!" % nickname)

                    # Construct welcome message to send back to this specific client
                    message = str.encode('Welcome %s! '
                                         'If you ever want to quit, type \'{quit}\' within the chat client to exit.' % nickname)

                    # Send welcome message to this specific client
                    server_socket.sendto(message, address)

                    # Continue iterating, after adding the client
                    continue
                else:
                    # If nickname already exists within the list of connected clients,
                    # then someone is already using that name

                    # Send a message back to the client indicating that this
                    # nickname is already taken and to choose another one
                    server_socket.sendto(str.encode(self.NICKNAME_ALREADY_EXISTS_MESSAGE, 'utf-8'), address)

                    # Continue iterating, after rejecting nickname
                    continue
            else:
                # The last sequence # associated with this client
                last_sequence_num = self.clients[nickname][1]

                # Check if this client has timed-out, if he or she
                # hasn't acknowledged the last 3 or more messages sent
                # to the server
                if (current_sequence_num - last_sequence_num) >= 3:
                    # Show that the server is dropping this client
                    print("[-] 🖥 Client (%s, '%s', %s): has disconnected" % (nickname, addr, port))

                    # If the client has timed-out, remove them from the chat
                    del self.clients[nickname]

                    # Continue iterating, after removing the client
                    continue

                # Update the current sequence number
                current_sequence_num = current_sequence_num + 1

                # Check if the client has left the chat
                if message.lower() != self.QUIT_MESSAGE.lower():
                    # Construct the message to send to the client
                    message = '%s > %s' % (nickname, message)

                    # If client has not left chat, broadcast the received message
                    self.broadcast(server_socket, message)
                else:
                    # If client has left chat, because he or she has entered '{quit}':

                    # Show that the client has disconnected
                    print("[-] 🖥 Client (%s, '%s', %s): has disconnected" % (nickname, addr, port))

                    # Remove the client from the client's list
                    del self.clients[nickname]

                    if len(self.clients) > 0:
                        # Continue iterating, after removing the client
                        continue
                    else:
                        # If there aren't any clients connected, break and exit
                        break

                # Update the client's last sequence number
                self.clients[nickname] = [address, current_sequence_num]

    @staticmethod
    def decode_message(data):
        """Decodes a message from the client"""

        # Split the message into a ',' separated list
        data = str(data.decode('utf-8')).split(',')

        # Parse the message to obtain:

        # The client's nickname
        nickname = data[0]
        # The client's message
        message = data[1]

        return nickname, message

    def broadcast(self, server_socket, message):
        """Broadcast a message to all connected clients"""

        for nickname in self.clients:
            # Obtain (address, port) tuple of the client
            client = self.clients[nickname][0]

            # Check if the message is not already a byte-stream
            if type(message) is not bytes:
                # If the message is not a byte-stream, then
                # encode the message
                message = str.encode(message, 'utf-8')

            # Send message to client
            server_socket.sendto(message, client)


if __name__ == '__main__':
    Server('127.0.0.1', 4096)
