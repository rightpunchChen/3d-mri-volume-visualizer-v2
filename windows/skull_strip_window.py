from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import (
    QWidget, QSpinBox, QGridLayout, QLabel, QPushButton, QRadioButton, QSlider, QComboBox
)
from windows.drop_line import DropLineEdit

class SkullStrip_Window(object):
    def __init__(self, centralwidget):
        self.ss_panel = QWidget(centralwidget)
        self.ss_panel.setObjectName("ss_panel")
        self.ss_panel.setFixedSize(360,150)

        self.ss_layout = QGridLayout(centralwidget)

        self.input_image = QLabel("input Image:", self.ss_panel)
        self.input_image.setObjectName("input_image")
        self.input_image.setGeometry(QRect(5, 40, 85, 21))
        self.input_image_lineEdit = DropLineEdit(self.ss_panel)
        self.input_image_lineEdit.setObjectName("input_image_lineEdit")
        self.input_image_lineEdit.setGeometry(QRect(100, 40, 200, 21))
        self.input_image_lineEdit.setClearButtonEnabled(False)
        self.input_image_btn = QPushButton("^", self.ss_panel)
        self.input_image_btn.setObjectName("input_image_btn")
        self.input_image_btn.setGeometry(QRect(300, 35, 48, 32))


        self.skullstrip_btn = QPushButton("SkullStrip", self.ss_panel)
        self.skullstrip_btn.setObjectName("skullstrip_btn")
        self.skullstrip_btn.setGeometry(QRect(130, 100, 113, 32))
        self.skullstrip_btn.setEnabled(False)

        self.ss_layout.addWidget(self.ss_panel, 0, 0, 1, 1)