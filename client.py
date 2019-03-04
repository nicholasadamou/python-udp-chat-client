from tkinter import *
from tkinter import messagebox

import socket
import threading
import re

# Types of messages sent by the client
NEW_CLIENT_MESSAGE = '{NEW CLIENT REQUEST}'  # Used to indicated a new client is connecting to the server
QUIT_MESSAGE = '{QUIT}'  # Used to indicate a client is leaving the chat
NICKNAME_ALREADY_EXISTS_MESSAGE = '{NICKNAME ALREADY EXISTS}'  # Used to indicate that the nickname already exists
BLANK_MESSAGE = ''  # Used to indicate a totally blank message


class Login(Tk):
    BUFFER_SIZE = 4096
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, server):
        super().__init__()

        # The (address, port) tuple of the server
        self.server = server

        # Demuxify the server (address, port) tuple
        self.server_addr, self.server_port = self.server

        # Set the title of the window
        self.title('Chat Client Login')

        # Make window auto-focus
        self.attributes('-topmost', True)

        # Center the window on the screen
        center_window(self, 250, 70)

        # Prevent the resizing of the window
        self.resizable(0, 0)

        # Bind 'escape' to the close event
        self.bind('<Escape>', self.on_window_close)
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # The username of the client
        self.nickname = StringVar()

        # The label to display 'Nickname:'
        self.nickname_label = Label(self, text='Nickname:', font=('Operator Mono', 14))
        self.nickname_label.pack(fill=X)
        self.nickname_label.place(relx=0, rely=0.11)

        # The input field for the client to enter a nickname
        self.nickname_entry = Entry(self, textvariable=self.nickname)
        self.nickname_entry.pack()
        self.nickname_entry.place(relwidth=0.7, relx=0.30, rely=0.10)
        self.nickname_entry.focus()

        # The 'Join Chat' button
        self.connect_button = Button(self, text='Join Chat', font=('Operator Mono', 14), command=self.on_connect)
        self.connect_button.bind('<Return>', self.on_connect)
        self.connect_button.pack(expand=1, fill=X)
        self.connect_button.place(relx=0.25, rely=0.55)

    def on_connect(self):
        """Handles the 'on connect' event"""

        # Obtain the client's entered username from the username entry field
        nickname = self.nickname_entry.get()

        if not nickname:
            # Nickname field must be filled out
            messagebox.showwarning('Warning', 'Nickname field must be filled before proceeding.')
        elif Login.is_valid_nickname(nickname):
            # Nickname must follow certain guidelines
            messagebox.showwarning('Warning',
                                   'Nickname is not valid. '
                                   'It must not contain any spaces or special characters.')

            # Clear the nickname field
            self.nickname.set('')
        else:
            # Connect to the chat server
            self.connect()

    def connect(self):
        """Connects to the chat server"""

        # Choose a unique nickname
        nickname = self.nickname_entry.get()

        # Determine if the nickname does not already exist
        if not self.does_nickname_already_exist(nickname):
            # Show that the client has successfully connected
            print("[!] 🖥️ Client (%s, '%s', %s): has connected" % (nickname, self.server_addr, self.server_port))

            # Close the login window
            self.on_window_close()

            # Open the Chat Client window
            Client(nickname, self.client_socket, self.server).mainloop()
        else:
            # If the nickname is not unique, then:

            # Close the login window
            self.on_window_close()

            # Create & open a new client login application window to try again
            Login(('127.0.0.1', 4096)).mainloop()

    def on_window_close(self):
        """Closes and terminates the root window of this application"""

        self.destroy()

    def does_nickname_already_exist(self, nickname):
        """Determines if the client's chosen nickname already exists within the
        chat server's connected client list"""

        # Construct the client payload to be sent to the chat server
        payload = encode(nickname, NEW_CLIENT_MESSAGE)

        # Send the payload to the chat server
        self.client_socket.sendto(payload, self.server)

        # Obtain the response message from the chat server
        response, server_addr = self.client_socket.recvfrom(self.BUFFER_SIZE)

        # Decode the response byte-stream
        response = response.decode('utf-8')

        # Check if the response indicates that the nickname already exists
        if response == NICKNAME_ALREADY_EXISTS_MESSAGE:
            # Show that the nickname already exists
            messagebox.showerror('Error', 'Nickname is already taken.')
            print("[!] ('%s'): is already taken." % nickname)

            # Clear the nickname entry field
            self.nickname.set('')

            # Nickname is not unique and exits within the server's
            # connected client list
            return True
        else:
            # Nickname is unique and does not exist within the server's
            # connected client list
            return False

    @staticmethod
    def is_valid_nickname(nickname):
        """Makes sure the nickname is valid"""

        # RULES:
        # NO spaces
        # No special characters
        return re.search("[^a-zA-Z0-9]+", nickname)


# -----------------------------------------

class Client(Tk):
    # The size of the buffer to receive data from chat server
    BUFFER_SIZE = 4096

    def __init__(self, nickname, client_socket, server):
        super().__init__()

        # The nickname of the client
        self.nickname = nickname

        # The connection between the client and the chat server
        self.client_socket = client_socket

        # The (address, port) tuple of the server
        self.server = server

        # Demuxify the server (address, port) tuple
        self.server_addr, self.server_port = self.server

        # Set the title of the window
        self.title('%s\'s Chat Client' % nickname)

        # Make window auto-focus
        self.attributes('-topmost', True)

        # Center the window on the screen
        center_window(self, 500, 300)

        # Prevent the resizing of the window
        self.resizable(0, 0)

        # Bind 'escape' to the close event
        self.bind('<Escape>', self.on_window_close)
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # The scrollbar for the message feed
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack()
        self.scrollbar.place(relx=1, rely=0.85)

        # The feed where messages are displayed
        self.feed = Text(self, yscrollcommand=self.scrollbar.set, font=('Operator Mono', 14))
        self.feed.pack()
        self.feed.place(relheight=0.85, relwidth=1, relx=0, rely=0)

        # Configure the scrollbar to use the message feed
        self.scrollbar.config(command=self.feed.yview)

        # The label to display 'Message:'
        self.username_label = Label(self, text='Message:', font=('Operator Mono', 14))
        self.username_label.pack(fill=X)
        self.username_label.place(relx=0.01, rely=0.9)

        # The message to send to the chat server
        self.message = StringVar()
        self.message_entry = Entry(self, textvariable=self.message, width=32)
        self.message_entry.pack()
        self.message_entry.place(relx=0.15, rely=0.89)
        self.message_entry.focus()

        # The send button
        self.message_button = Button(self, text='Send Message', font=('Operator Mono', 14), command=self.on_submit)
        self.message_button.pack()
        self.message_button.place(relx=0.75, rely=0.89)

        # Start the thread to handle receiving of messages
        threading.Thread(target=self.receive_message, args=(self.client_socket,)).start()

    def on_window_close(self):
        """Closes and terminates the root window of this application"""

        self.message.set('{quit}')
        self.send_message(self.client_socket)
        self.destroy()
        sys.exit(0)

    def on_submit(self):
        """Handles the 'on submit' event"""

        self.send_message(self.client_socket)

    def send_message(self, client_socket):
        """Handles sending messages to the chat server"""

        # Client entered a new message
        message = self.message.get()

        # Clear input field
        self.message.set('')

        # Construct a the client payload
        payload = encode(self.nickname, message)

        # Attempt to send a message to the chat server
        try:
            client_socket.sendto(payload, self.server)
        except socket.error:
            # If there is an error with the socket, then pass
            pass

        # Show the message
        print("[*] [SENT] %s > %s" % (self.nickname, message))

        if message.lower() == QUIT_MESSAGE.lower():
            # If message is '{quit}', then close the client connection and quit
            print("[!] 🖥️ Client (%s, '%s', %s): has disconnected" % (self.nickname, self.server_addr, self.server_port))
            client_socket.close()
            sys.exit(0)

    def receive_message(self, server_socket):
        """Handles receiving a message from the chat server"""

        while 1:
            # Attempt to receive a message from the chat server
            try:
                # Obtain the message and address sent by the chat server
                message, address = server_socket.recvfrom(self.BUFFER_SIZE)

                # Check if the message exists
                if message:
                    # Decode the byte-stream message into a utf-8 string
                    message = message.decode('utf-8')

                    # Do not print the NICKNAME_ALREADY_EXISTS_MESSAGE message to the feed
                    if message.lower() != NICKNAME_ALREADY_EXISTS_MESSAGE.lower():
                        # Set the state of the feed to 'normal' so it can insert the
                        # received message from the chat server
                        self.feed.config(state='normal')
                        # Insert recent message to the END of the message feed
                        self.feed.insert(END, message + '\n')
                        # Disable the feed after inserting the message into the feed
                        # so that the client cannot insert text or manipulate the
                        # text within it
                        self.feed.config(state='disabled')

                        # Show the received message
                        print("[*] [RECEIVED] %s" % message)
            except socket.error:
                # If there is an error with the socket, then break
                break

# -----------------------------------------


def encode(nickname, message):
    """Encodes a message as a comma separated list to be sent to the chat server"""

    # Construct the payload
    payload = '%s,%s' % (nickname, message)

    # Encode the payload as utf-8 byte stream, so it can be sent to the chat server
    return str.encode(payload, 'utf-8')


def center_window(parent, width, height):
    """Calculates the center of the screen based off of the inputted
    width and height, then centers the frame on the screen using those
    coordinates"""

    # Get the screen width and height
    window_width = parent.winfo_screenwidth()
    window_height = parent.winfo_screenheight()

    # Calculate  the xCenter and yCenter coordinates
    xCenter = (window_width / 2) - (width / 2)
    yCenter = (window_height / 2) - (height / 2)

    # Center the window on the screen
    parent.geometry('%dx%d+%d+%d' % (width, height, xCenter, yCenter))


# -----------------------------------------

if __name__ == '__main__':
    # Create & open the client login application window
    Login(('127.0.0.1', 4096)).mainloop()
