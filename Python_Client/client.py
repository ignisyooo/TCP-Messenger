import socket
from windows import MainWindow
from threading import Thread

class Client(MainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self._socket = None
        self.connected = False

        self.insert_text(f'User created: {self.username}')

    @property
    def socket(self):
        return self._socket

    @socket.setter
    def socket(self, value):
        self._socket = value

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect(("192.168.0.164", 7))
            self.connected = True
            self.insert_text('Connected.')
            self.receive()
        except ConnectionRefusedError:
            self.insert_text('The server is not online.')

    def receive(self):
        while self.connected:
            try:
                data = str(self.socket.recv(1024).decode("utf-8", "ignore"))
                if len(data) == 0:
                    pass
                else:
                    self.insert_text(data)
            except ConnectionAbortedError:
                self.insert_text('Disconnected')
                self.connected = False

    def send(self):
        message = self.username + ': ' + self.text
        try:
            self.socket.sendall(bytes(message.encode("utf-8", "ignore")))
            self.insert_text(message)
            self.text_window.clear()
        except BrokenPipeError:
            self.insert_text("Server has been disconnected.\n")
            self.socket.close()
        except TimeoutError:
            self.insert_text("Connection to the server was lost. Please try again.\n")

    def create_connection(self):
        self.connect_button.setText('Disconnect')
        thread_connection = Thread(target=self.connect)
        thread_connection.start()

    def remove_connection(self):
        self.close_connection()
        self.connect_button.setText('Connect')

    def send_text(self):
        if self.connected:
            self.send()
        else:
            self.insert_text("First, you need to make connections\n")

    def close_connection(self):
        if self.connected:
            self.connected = False
            self.socket.close()