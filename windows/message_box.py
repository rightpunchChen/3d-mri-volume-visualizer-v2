from PySide6.QtWidgets import QMessageBox

def show_error_message(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText(message)
    msg_box.setWindowTitle("Error")
    msg_box.exec()