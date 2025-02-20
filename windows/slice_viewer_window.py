from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import (
    QWidget, QSpinBox, QLabel, QPushButton, QRadioButton, QSlider, QComboBox
)
from windows.drop_line import DropLineEdit

class SliceViewer_Window(object):
    def __init__(self, centralwidget):
        self.sv_panel = QWidget(centralwidget)
        self.sv_panel.setObjectName("sv_panel")
        self.sv_panel.setFixedWidth(320)

        self.BF_label = QLabel("Image File:", self.sv_panel)
        self.BF_label.setObjectName("BF_label")
        self.BF_label.setGeometry(QRect(20, 40, 60, 21))
        self.BF_lineEdit = DropLineEdit(self.sv_panel)
        self.BF_lineEdit.setObjectName("BF_lineEdit")
        self.BF_lineEdit.setGeometry(QRect(90, 40, 161, 21))
        self.BF_lineEdit.setClearButtonEnabled(False)
        self.BF_btn = QPushButton("^", self.sv_panel)
        self.BF_btn.setObjectName("BF_btn")
        self.BF_btn.setGeometry(QRect(253, 35, 48, 32))

        self.LF_label = QLabel("Label File:", self.sv_panel)
        self.LF_label.setObjectName("LF_label")
        self.LF_label.setGeometry(QRect(20, 70, 60, 21))
        self.LF_lineEdit = DropLineEdit(self.sv_panel)
        self.LF_lineEdit.setObjectName("LF_lineEdit")
        self.LF_lineEdit.setGeometry(QRect(90, 70, 161, 21))
        self.LF_lineEdit.setEnabled(False)
        self.LF_lineEdit.setClearButtonEnabled(False)
        self.LF_btn = QPushButton("^", self.sv_panel)
        self.LF_btn.setObjectName("LF_btn")
        self.LF_btn.setGeometry(QRect(253, 65, 48, 32))
        self.LF_btn.setEnabled(False)

        self.PF_label = QLabel("Pred File:", self.sv_panel)
        self.PF_label.setObjectName("PF_label")
        self.PF_label.setGeometry(QRect(20, 100, 60, 21))
        self.PF_lineEdit = DropLineEdit(self.sv_panel)
        self.PF_lineEdit.setObjectName("PF_lineEdit")
        self.PF_lineEdit.setGeometry(QRect(90, 100, 161, 21))
        self.PF_lineEdit.setEnabled(False)
        self.PF_lineEdit.setClearButtonEnabled(False)
        self.PF_btn = QPushButton("^", self.sv_panel)
        self.PF_btn.setObjectName("PF_btn")
        self.PF_btn.setGeometry(QRect(253, 95, 48, 32))
        self.PF_btn.setEnabled(False)

        self.label_label = QLabel("Label", self.sv_panel)
        self.label_label.setObjectName("label_label")
        self.label_label.setGeometry(QRect(20, 150, 60, 21))

        self.radioButton_1 = QRadioButton("1", self.sv_panel)
        self.radioButton_1.setObjectName("radioButton_1")
        self.radioButton_1.setGeometry(QRect(70, 150, 41, 20))
        self.radioButton_1.setEnabled(False)
        self.radioButton_1.setAutoExclusive(False)
        self.radioButton_2 = QRadioButton("2", self.sv_panel)
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_2.setGeometry(QRect(110, 150, 41, 20))
        self.radioButton_2.setEnabled(False)
        self.radioButton_2.setAutoExclusive(False)
        self.radioButton_3 = QRadioButton("3", self.sv_panel)
        self.radioButton_3.setObjectName("radioButton_3")
        self.radioButton_3.setGeometry(QRect(150, 150, 41, 20))
        self.radioButton_3.setEnabled(False)
        self.radioButton_3.setAutoExclusive(False)
        self.radioButton_4 = QRadioButton("4", self.sv_panel)
        self.radioButton_4.setObjectName("radioButton_4")
        self.radioButton_4.setGeometry(QRect(190, 150, 41, 20))
        self.radioButton_4.setEnabled(False)
        self.radioButton_4.setAutoExclusive(False)
        self.radioButton_5 = QRadioButton("5", self.sv_panel)
        self.radioButton_5.setObjectName("radioButton_5")
        self.radioButton_5.setGeometry(QRect(230, 150, 41, 20))
        self.radioButton_5.setEnabled(False)
        self.radioButton_5.setAutoExclusive(False)

        self.label_op_label = QLabel("Label Opacity", self.sv_panel)
        self.label_op_label.setObjectName("label_op_label")
        self.label_op_label.setGeometry(QRect(20, 180, 91, 21))
        self.LO_spinBox = QSpinBox(self.sv_panel)
        self.LO_spinBox.setObjectName("LO_spinBox")
        self.LO_spinBox.setGeometry(QRect(110, 180, 61, 24))
        self.LO_spinBox.setMinimum(1)
        self.LO_spinBox.setMaximum(40)
        self.LO_spinBox.setValue(20)
        self.LO_spinBox.setSingleStep(1)
        self.LO_spinBox.setEnabled(False)

        self.pred_label = QLabel("Pred", self.sv_panel)
        self.pred_label.setObjectName("pred_label")
        self.pred_label.setGeometry(QRect(20, 230, 60, 21))

        self.radioButton_tp = QRadioButton("TP", self.sv_panel)
        self.radioButton_tp.setObjectName("radioButton_tp")
        self.radioButton_tp.setGeometry(QRect(70, 230, 41, 20))
        self.radioButton_tp.setEnabled(False)
        self.radioButton_tp.setAutoExclusive(False)
        self.radioButton_fp = QRadioButton("FP", self.sv_panel)
        self.radioButton_fp.setObjectName("radioButton_fp")
        self.radioButton_fp.setGeometry(QRect(120, 230, 41, 20))
        self.radioButton_fp.setEnabled(False)
        self.radioButton_fp.setAutoExclusive(False)
        self.radioButton_fn = QRadioButton("FN", self.sv_panel)
        self.radioButton_fn.setObjectName("radioButton_fn")
        self.radioButton_fn.setGeometry(QRect(170, 230, 41, 20))
        self.radioButton_fn.setEnabled(False)
        self.radioButton_fn.setAutoExclusive(False)

        self.pred_op_label = QLabel("Pred Opacity", self.sv_panel)
        self.pred_op_label.setObjectName("pred_op_label")
        self.pred_op_label.setGeometry(QRect(20, 260, 91, 21))
        self.PO_spinBox = QSpinBox(self.sv_panel)
        self.PO_spinBox.setObjectName("PO_spinBox")
        self.PO_spinBox.setGeometry(QRect(110, 260, 61, 24))
        self.PO_spinBox.setMinimum(1)
        self.PO_spinBox.setMaximum(40)
        self.PO_spinBox.setValue(20)
        self.PO_spinBox.setSingleStep(1)
        self.PO_spinBox.setEnabled(False)

        self.ot_label = QLabel("Orientation", self.sv_panel)
        self.ot_label.setObjectName(u"ot_label")
        self.ot_label.setGeometry(QRect(20, 310, 90, 16))
        self.slice_comboBox = QComboBox(self.sv_panel)
        self.slice_comboBox.addItem("axial (xy)")
        self.slice_comboBox.addItem("sagittal (yz)")
        self.slice_comboBox.addItem("coronal (xz)")
        self.slice_comboBox.setObjectName(u"slice_comboBox")
        self.slice_comboBox.setGeometry(QRect(105, 305, 120, 26))
        self.slice_comboBox.setEnabled(False)

        self.slice_horizontalSlider = QSlider(self.sv_panel)
        self.slice_horizontalSlider.setObjectName(u"slice_horizontalSlider")
        self.slice_horizontalSlider.setGeometry(QRect(20, 370, 280, 22))
        self.slice_horizontalSlider.setOrientation(Qt.Horizontal)
        self.slice_horizontalSlider.setEnabled(False)

        self.slice_label = QLabel("Slice:", self.sv_panel)
        self.slice_label.setObjectName(u"slice_label")
        self.slice_label.setGeometry(QRect(20, 340, 41, 16))
        self.slice_idx_label = QLabel(self.sv_panel)
        self.slice_idx_label.setObjectName(u"slice_idx_label")
        self.slice_idx_label.setGeometry(QRect(60, 340, 41, 16))

        self.render_pushButton = QPushButton("Render", self.sv_panel)
        self.render_pushButton.setObjectName("render_pushButton")
        self.render_pushButton.setGeometry(QRect(95, 430, 113, 32))
        self.render_pushButton.setEnabled(False)

        self.savePNG_pushButton = QPushButton("Save PNG", self.sv_panel)
        self.savePNG_pushButton.setObjectName("savePNG_pushButton")
        self.savePNG_pushButton.setGeometry(QRect(30, 480, 113, 32))
        self.savePNG_pushButton.setEnabled(False)

        self.saveMP4_pushButton = QPushButton("Save MP4", self.sv_panel)
        self.saveMP4_pushButton.setObjectName("saveMP4_pushButton")
        self.saveMP4_pushButton.setGeometry(QRect(160, 480, 113, 32))
        self.saveMP4_pushButton.setEnabled(False)