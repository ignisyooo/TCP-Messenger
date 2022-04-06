from threading import Thread
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QPushButton, QGridLayout, QTextEdit
from PyQt5.QtCore import QSize, Qt

class ButtonError(Exception):
    """Raised when the button value is not correct"""
    pass

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.UiComponents()

    def UiComponents(self) -> None:
        self.setMinimumSize(QSize(400, 800))
        self.setWindowTitle('Messenger')

        layout = QGridLayout()

        self.log_window = QTextEdit() # noqa
        self.log_window.setGeometry(QtCore.QRect(30, 40, 431, 441))

        font = QtGui.QFont()
        font.setFamily("Segoe UI Symbol")
        font.setPointSize(9)

        self.log_window.setFont(font)
        self.log_window.setReadOnly(True)

        layout.addWidget(self.log_window)

        self.text_window = QLineEdit(self) # noqa
        self.text_window.setGeometry(QtCore.QRect(600, 40, 431, 441))
        self.text_window.returnPressed.connect(self.send_text)

        layout.addWidget(self.text_window)

        self.send_button = QPushButton('Send') # noqa
        self.send_button.clicked.connect(self.send_text)

        self.connect_button = QPushButton('Connect') # noqa
        self.connect_button.clicked.connect(self.connection_button_action)

        self.clear_button = QPushButton('Clear') # noqa
        self.clear_button.clicked.connect(self.clear)

        layout.addWidget(self.send_button)
        layout.addWidget(self.clear_button, 0, 1)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def insert_text(self, text):
        time = datetime.now()
        text = '[' + time.strftime('%Y-%m-%d %H:%M:%S') + '] ' + text + '\n'
        self.log_window.insertPlainText(text)

    def connection_button_action(self):
        action = self.connect_button.text()
        match action:
            case 'Connect': self.create_connection()
            case 'Disconnect': self.remove_connection()
            case _:
                raise ButtonError('Invalid action for the button')

    @property
    def text(self):
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

    """Abstract methods"""
    def create_connection(self):
        pass

    def remove_connection(self):
        pass

    def send_text(self, text):
        pass

    def close_connection(self):
        pass


class Login(QWidget):
    """First Windows with login section"""
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.UiComponents()

    def UiComponents(self) -> None:
        """Create UI"""
        self.setMinimumSize(QSize(320, 140))
        self.setWindowTitle('Login')

        nameLabel = QLabel(self) # noqa
        nameLabel.setText('Username')
        nameLabel.move(140, 20)

        self.line = QLineEdit(self) # noqa
        self.line.setAlignment(Qt.AlignCenter)
        self.line.returnPressed.connect(self.login)

        self.line.move(80, 50)
        self.line.resize(200, 32)

        button = QPushButton('LogIn', self)
        button.clicked.connect(self.login)
        button.resize(200, 32)
        button.move(80, 100)


    def login(self) -> None:
        """LogIn button action

        Function take username from QLine and pass it to MainWindow
        """
        username = self.line.text()
        self.switch_window.emit(username)
