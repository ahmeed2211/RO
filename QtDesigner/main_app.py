import sys
from PyQt5 import QtWidgets
from MainInterface import Ui_MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(win)

    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()