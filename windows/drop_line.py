from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit

class DropLineEdit(QLineEdit):
    textDropped = Signal(str)

    def __init__(self, parent=None, file_type=('.nii', '.nii.gz')):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.file_type = file_type

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(self.file_type):
                self.setText(file_path)
                self.textDropped.emit(file_path)
                break
