import sys
from threading import Thread
from PyQt5 import QtWidgets

from windows import Login
from client import Client

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
    assert sys.version_info >= (3, 10, 0), \
                'Python 3.10 is required'
    main_thread = Thread(target=main)
    main_thread.run()
