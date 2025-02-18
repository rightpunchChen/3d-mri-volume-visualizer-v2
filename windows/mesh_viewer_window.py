from PySide6.QtCore import QRect
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QPushButton
)
from windows.drop_line import DropLineEdit

class MeshViewer_Window(object):
    def __init__(self, centralwidget):
        self.mv_panel = QWidget(centralwidget)
        self.mv_panel.setObjectName("msv_panel")
        self.mv_panel.setFixedSize(360, 150)

        self.msv_layout = QGridLayout(centralwidget)

        self.mesh_data_label = QLabel("Mesh File:", self.mv_panel)
        self.mesh_data_label.setObjectName("mesh_data_label")
        self.mesh_data_label.setGeometry(QRect(5, 40, 75, 21))
        self.mesh_data_lineEdit = DropLineEdit(self.mv_panel)
        self.mesh_data_lineEdit.setObjectName("mesh_data_lineEdit")
        self.mesh_data_lineEdit.setGeometry(QRect(90, 40, 200, 21))
        self.mesh_data_lineEdit.setClearButtonEnabled(False)
        self.mesh_data_btn = QPushButton("^", self.mv_panel)
        self.mesh_data_btn.setObjectName("mesh_data_btn")
        self.mesh_data_btn.setGeometry(QRect(300, 35, 48, 32))

        self.render_btn = QPushButton("Render", self.mv_panel)
        self.render_btn.setObjectName("render_btn")
        self.render_btn.setGeometry(QRect(130, 70, 113, 32))
        self.render_btn.setEnabled(False)

        self.msv_layout.addWidget(self.mv_panel, 0, 0, 1, 1)
