from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt
def show_error_message(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText(message)
    msg_box.setWindowTitle("Error")
    msg_box.exec()

def show_info_message(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    msg_box.setWindowTitle("Information")
    msg_box.setWindowFlag(Qt.WindowStaysOnTopHint)  # 讓訊息框保持在最上層
    msg_box.exec()