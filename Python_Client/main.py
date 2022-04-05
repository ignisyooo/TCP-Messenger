import sys
from datetime import datetime
import socket
from threading import Thread
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QPushButton, QGridLayout, QTextEdit
from PyQt5.QtCore import QSize, Qt


class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setMinimumSize(QSize(400, 800))
        self.setWindowTitle('Messenger')

        layout = QGridLayout()

        self.log_window = QTextEdit()
        self.log_window.setGeometry(QtCore.QRect(30, 40, 431, 441))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(9)
        self.log_window.setFont(font)
        self.log_window.setReadOnly(True)
        layout.addWidget(self.log_window)

        self.text_window = QLineEdit(self)
        self.text_window.setGeometry(QtCore.QRect(600, 40, 431, 441))
        self.text_window.returnPressed.connect(self.send_text)

        layout.addWidget(self.text_window)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_text)

        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.create_connection)

        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.clear)

        layout.addWidget(self.send_button)
        layout.addWidget(self.clear_button, 0, 1)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def insert_text(self, text):
        time = datetime.now()
        text = '[' + time.strftime('%Y-%m-%d %H:%M:%S') + '] ' + text + '\n'
        self.log_window.insertPlainText(text)

    def create_connection(self):
        pass

    def send_text(self, text):
        pass

    def close_connection(self):
        pass

    def get_text(self):
        return self.text_window.text()

    def clear(self):
        self.log_window.clear()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close_connection()
            event.accept()
        else:
            event.ignore()


class Client(MainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.insert_text(f'User created: {self.username}')
        self.connected = False

    @property
    def socket(self):
        return self._socket

    def connect(self):
        try:
            self.socket.connect(("192.168.0.164", 8))
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
                self.insert_text('Connection interrupted.')
                self.connected = False

    def send(self):
        text = self.get_text()
        message = self.username + ': ' + text
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
        thread_connection = Thread(target=self.connect)
        thread_connection.start()

    def send_text(self):
        if self.connected:
            self.send()
        else:
            self.insert_text("First, you need to make connections\n")

    def close_connection(self):
        if self.connected:
            self.connected = False
            self.socket.close()


class Login(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setMinimumSize(QSize(320, 140))
        self.setWindowTitle('Login')

        self.nameLabel = QLabel(self)
        self.nameLabel.setText('Username')
        self.line = QLineEdit(self)
        self.line.setAlignment(Qt.AlignCenter)
        self.line.returnPressed.connect(self.login)

        self.line.move(80, 50)
        self.line.resize(200, 32)
        self.nameLabel.move(140, 20)

        self.button = QPushButton('LogIn', self)
        self.button.clicked.connect(self.login)
        self.button.resize(200, 32)
        self.button.move(80, 100)

    def login(self):
        username = self.line.text()
        self.switch_window.emit(username)


class Controller:
    login: Login
    main_window: Client

    def __init__(self):
        self.login = Login()
        self.main_window = None

    def show_login(self):
        self.login = Login()
        self.login.switch_window.connect(self.show_main)
        self.login.show()

    def show_main(self, username: str) -> None:
        self.main_window = Client(username)
        self.login.close()
        self.main_window.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main_thread = Thread(target=main)
    main_thread.run()
