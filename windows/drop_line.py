from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit

class DropLineEdit(QLineEdit):
    textDropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.nii', '.nii.gz')):
                self.setText(file_path)
                self.textDropped.emit(file_path)
                break