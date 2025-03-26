from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import (
    QWidget, QSpinBox, QGridLayout, QLabel, QPushButton, QRadioButton, QSlider, QComboBox
)
from windows.drop_line import DropLineEdit
import itk 
import SimpleITK as sitk

class Registration_Window(object):
    def __init__(self, centralwidget):
        self.reg_panel = QWidget(centralwidget)
        self.reg_panel.setObjectName("reg_panel")
        self.reg_panel.setFixedSize(360,150)

        self.reg_layout = QGridLayout(centralwidget)

        self.fixed_image = QLabel("Fixed Image:", self.reg_panel)
        self.fixed_image.setObjectName("fixed_image")
        self.fixed_image.setGeometry(QRect(5, 40, 85, 21))
        self.fixed_image_lineEdit = DropLineEdit(self.reg_panel)
        self.fixed_image_lineEdit.setObjectName("fixed_image_lineEdit")
        self.fixed_image_lineEdit.setGeometry(QRect(100, 40, 200, 21))
        self.fixed_image_lineEdit.setClearButtonEnabled(False)
        self.fixed_image_btn = QPushButton("^", self.reg_panel)
        self.fixed_image_btn.setObjectName("fixed_image_btn")
        self.fixed_image_btn.setGeometry(QRect(300, 35, 48, 32))

        self.moving_image = QLabel("Moving Image:", self.reg_panel)
        self.moving_image.setObjectName("moving_image")
        self.moving_image.setGeometry(QRect(5, 70, 85, 21))
        self.moving_image_lineEdit = DropLineEdit(self.reg_panel)
        self.moving_image_lineEdit.setObjectName("moving_image_lineEdit")
        self.moving_image_lineEdit.setGeometry(QRect(100, 70, 200, 21))
        self.moving_image_lineEdit.setClearButtonEnabled(False)
        self.moving_image_btn = QPushButton("^", self.reg_panel)
        self.moving_image_btn.setObjectName("moving_image_btn")
        self.moving_image_btn.setGeometry(QRect(300, 65, 48, 32))

        self.registration_btn = QPushButton("Registration", self.reg_panel)
        self.registration_btn.setObjectName("registration_btn")
        self.registration_btn.setGeometry(QRect(130, 100, 113, 32))
        self.registration_btn.setEnabled(False)

        self.reg_layout.addWidget(self.reg_panel, 0, 0, 1, 1)

        


        