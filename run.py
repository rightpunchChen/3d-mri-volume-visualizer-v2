from PySide6 import QtWidgets
from controllers.controller import MainWindowController

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    viewer = MainWindowController()
    viewer.show()
    app.exec()