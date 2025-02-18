import numpy as np
import SimpleITK as sitk
from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import (
    QApplication, QComboBox, QLabel, QPushButton,
    QRadioButton, QSizePolicy, QSlider, QSpinBox,
    QVBoxLayout, QWidget, QFileDialog
    )
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from windows.message_box import show_error_message


class MultiImgSliceViewer(QWidget):
    def __init__(self, data_list, label_list, colors):
        super().__init__()
        self.data_list = data_list
        self.label_list = label_list
        self.labeled_image_list = []
        self.colors = colors

        self.num_plots = len(data_list)
        self.num_rows = 1 
        self.num_cols = len(data_list)
        self.fig, self.axes = plt.subplots(
            self.num_rows,
            self.num_cols,
            )
        if self.num_plots > 1 :
            self.axes = self.axes.ravel()
        self.fig.tight_layout()

        self.init_ui()
        self.init()

    def init_ui(self):
        self.centralwidget = QWidget()

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.canvas = FigureCanvas(self.fig)

        self.canvas_widget = QWidget(self.centralwidget)
        self.canvas_widget.setObjectName(u"canvas_widget")
        self.canvas_widget.setMinimumSize(300*self.num_cols, 200*self.num_rows)
        self.canvas_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        self.canvas_layout.setContentsMargins(0,0,0,0)
        self.canvas_layout.addWidget(self.canvas) 

        self.panel_widget = QWidget(self.centralwidget)
        self.panel_widget.setObjectName(u"panel_widget")
        self.panel_widget.setFixedSize(491, 191)

        self.savePNG_pushButton = QPushButton("Save PNG", self.panel_widget)
        self.savePNG_pushButton.setObjectName(u"savePNG_pushButton")
        self.savePNG_pushButton.setGeometry(QRect(240, 140, 113, 32))
        self.savePNG_pushButton.setEnabled(False)
        self.saveMP4_pushButton = QPushButton("Save MP4", self.panel_widget)
        self.saveMP4_pushButton.setObjectName(u"saveMP4_pushButton")
        self.saveMP4_pushButton.setGeometry(QRect(360, 140, 113, 32))
        self.saveMP4_pushButton.setEnabled(False)
        self.slice_horizontalSlider = QSlider(self.panel_widget)
        self.slice_horizontalSlider.setObjectName(u"slice_horizontalSlider")
        self.slice_horizontalSlider.setGeometry(QRect(30, 110, 431, 22))
        self.slice_horizontalSlider.setOrientation(Qt.Horizontal)
        self.slice_horizontalSlider.setEnabled(False)
        self.slice_label = QLabel("Slice:", self.panel_widget)
        self.slice_label.setObjectName(u"slice_label")
        self.slice_label.setGeometry(QRect(30, 80, 41, 16))
        self.slice_idx_label = QLabel(self.panel_widget)
        self.slice_idx_label.setObjectName(u"slice_idx_label")
        self.slice_idx_label.setGeometry(QRect(70, 80, 51, 16))
        self.comboBox = QComboBox(self.panel_widget)
        self.comboBox.addItem("axial (xy)")
        self.comboBox.addItem("sagittal (yz)")
        self.comboBox.addItem("coronal (xz)")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(120, 40, 101, 26))
        self.orientation_label = QLabel("Orientation", self.panel_widget)
        self.orientation_label.setObjectName(u"orientation_label")
        self.orientation_label.setGeometry(QRect(30, 40, 91, 21))
        self.label_label = QLabel("Label:", self.panel_widget)
        self.label_label.setObjectName(u"label_label")
        self.label_label.setGeometry(QRect(30, 10, 41, 21))
        self.lab_radioButton_1 = QRadioButton("1", self.panel_widget)
        self.lab_radioButton_1.setObjectName(u"lab_radioButton_1")
        self.lab_radioButton_1.setGeometry(QRect(80, 10, 31, 20))
        self.lab_radioButton_1.setAutoExclusive(False)
        self.lab_radioButton_1.setEnabled(False)
        self.lab_radioButton_2 = QRadioButton("2", self.panel_widget)
        self.lab_radioButton_2.setObjectName(u"lab_radioButton_2")
        self.lab_radioButton_2.setGeometry(QRect(120, 10, 31, 20))
        self.lab_radioButton_2.setAutoExclusive(False)
        self.lab_radioButton_2.setEnabled(False)
        self.lab_radioButton_3 = QRadioButton("3", self.panel_widget)
        self.lab_radioButton_3.setObjectName(u"lab_radioButton_3")
        self.lab_radioButton_3.setGeometry(QRect(160, 10, 31, 20))
        self.lab_radioButton_3.setAutoExclusive(False)
        self.lab_radioButton_3.setEnabled(False)
        self.lab_radioButton_4 = QRadioButton("4", self.panel_widget)
        self.lab_radioButton_4.setObjectName(u"lab_radioButton_4")
        self.lab_radioButton_4.setGeometry(QRect(200, 10, 31, 20))
        self.lab_radioButton_4.setAutoExclusive(False)
        self.lab_radioButton_4.setEnabled(False)
        self.lab_radioButton_5 = QRadioButton("5", self.panel_widget)
        self.lab_radioButton_5.setObjectName(u"lab_radioButton_5")
        self.lab_radioButton_5.setGeometry(QRect(240, 10, 31, 20))
        self.lab_radioButton_5.setAutoExclusive(False)
        self.lab_radioButton_5.setEnabled(False)
        self.op_label = QLabel("Opacity", self.panel_widget)
        self.op_label.setObjectName(u"op_label")
        self.op_label.setGeometry(QRect(250, 40, 91, 21))
        self.op_spinBox = QSpinBox(self.panel_widget)
        self.op_spinBox.setObjectName(u"op_spinBox")
        self.op_spinBox.setGeometry(QRect(310, 40, 51, 24))
        self.op_spinBox.setMinimum(0)
        self.op_spinBox.setMaximum(40)
        self.op_spinBox.setValue(20)
        self.op_spinBox.setEnabled(False)
        self.render_pushButton = QPushButton("Render", self.panel_widget)
        self.render_pushButton.setObjectName(u"render_pushButton")
        self.render_pushButton.setGeometry(QRect(30, 140, 113, 32))

        self.main_layout.addWidget(self.canvas_widget)
        self.main_layout.addWidget(self.panel_widget)
        self.setLayout(self.main_layout)

    def init(self):
        self.init_label_radioButton()
        self.render_pushButton.clicked.connect(self.render)
        self.slice_horizontalSlider.valueChanged.connect(self.set_slice)
        self.saveMP4_pushButton.clicked.connect(self.save_mp4)
        self.savePNG_pushButton.clicked.connect(self.save_png)
    
    def init_label_radioButton(self):
        max_label = 0
        for i in self.label_list:
            if i is None: continue
            tmp = i.astype(np.uint16).max()
            if tmp > max_label:
                max_label = tmp
        for i in range(1, min(max_label + 1, 6)):
            r = int(self.colors["MASK_COLORS"][i][0]*255)
            g = int(self.colors["MASK_COLORS"][i][1]*255)
            b = int(self.colors["MASK_COLORS"][i][2]*255)
            button = getattr(self, f'lab_radioButton_{i}')
            button.setStyleSheet(f"color: rgb({r}, {g}, {b});")
            button.setEnabled(True)

    def render(self):
        self.op_spinBox.setEnabled(True)
        self.slice_horizontalSlider.setEnabled(True)
        self.saveMP4_pushButton.setEnabled(True)
        self.savePNG_pushButton.setEnabled(True)
        self.slice_idx_label.setText("1")

        selected_label = []
        for i in range(1, 6):
            radio_button = getattr(self, f'lab_radioButton_{i}')
            if radio_button.isChecked():
                selected_label.append(i)

        self.labeled_image_list = []
        for i, data in enumerate(self.data_list):
            labeled_image = self.labeled_img(
                    data,
                    self.label_list[i],
                    label_value=selected_label,
                    alpha=self.op_spinBox.value() / 100)
            if self.comboBox.currentIndex() == 1:
                labeled_image = labeled_image.transpose(2, 1, 0, 3)[:, :, ::-1, :]
            elif self.comboBox.currentIndex() == 2:
                labeled_image = labeled_image.transpose(1, 0, 2, 3)[:, ::-1, :, :]
            self.labeled_image_list.append(labeled_image)

        self.images = []
        for i, data in enumerate(self.labeled_image_list):
            ax = self.axes[i] if self.num_plots > 1 else self.axes
            im = ax.imshow(data[0, :, :])
            self.images.append(im)

        self.slice_horizontalSlider.setMinimum(1)
        self.slice_horizontalSlider.setMaximum(self.data_list[0].shape[0]-1)
        self.slice_horizontalSlider.setValue(1)
        if self.num_plots > 1 :
            for i in range(self.num_plots, self.num_rows*self.num_cols):
                self.fig.delaxes(self.axes[i])
        self.canvas.draw()

    def normalize(self, matrix):
        min_val = np.min(matrix)
        max_val = np.max(matrix)
        normalized_matrix = (matrix - min_val) / (max_val - min_val)
        return normalized_matrix
    
    def labeled_img(self, data, label=None, label_value=[], alpha=0.2):
        data_norm = self.normalize(data)
        data_rgb = np.stack([data_norm] * 3, axis=-1)
        if label is None:
            return data_rgb
        color_mappings = self.colors["MASK_COLORS"]
        for lbl in label_value:
            mask = (label == lbl)
            color = np.array(color_mappings[lbl])
            data_rgb[mask] = (1 - alpha) * data_rgb[mask] + alpha * color
        return data_rgb

    def set_slice(self, val):
        slice_idx = int(val) - 1
        self.slice_idx_label.setText(f"{val}")
        for i, data in enumerate(self.labeled_image_list):
            self.images[i].set_data(data[slice_idx, :, :])
            ax = self.axes[i] if self.num_plots > 1 else self.axes
        self.canvas.draw()
    
    def save_mp4(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save MP4 file", "", "MP4 Files (*.mp4)")
        if file_path:
            if not file_path.endswith(('.mp4')):
                file_path = file_path + '.mp4'
            try:
                self.saveMP4_pushButton.setEnabled(False)

                def update(slice_idx):
                    for i, data in enumerate(self.labeled_image_list):
                        self.images[i].set_data(data[slice_idx, :, :])
                        ax = self.axes[i] if self.num_plots > 1 else self.axes
                    return self.images
                
                anim = FuncAnimation(
                    self.fig,
                    update,
                    frames=range(0, self.data_list[0].shape[0]),
                    interval=200,
                    blit=True
                    )
                anim.save(file_path, writer='ffmpeg', fps=30)
            except Exception as e:
                show_error_message(f"Error saving MP4: {e}")
            finally:
                self.saveMP4_pushButton.setEnabled(True)

    def save_png(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PNG file", "", "PNG Files (*.png)")
        if file_path:
            if not file_path.endswith('.png'):
                file_path = file_path + '.png'
            try:
                self.savePNG_pushButton.setEnabled(False)
                slice_idx = self.slice_horizontalSlider.value() - 1
                fig, ax = plt.subplots(figsize=(6, 6))
                ax.axis("off")
                for i, data in enumerate(self.labeled_image_list):
                    ax.imshow(data[slice_idx, :, :])
                fig.savefig(file_path, bbox_inches='tight', pad_inches=0, dpi=300)
                plt.close(fig)

            except Exception as e:
                show_error_message(f"Error saving PNG: {e}")
            finally:
                self.savePNG_pushButton.setEnabled(True)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    DEFAULT_COLORS = {
        "BACKGROUND_COLORS" : (0.82, 0.82, 0.82), # Background color
        "BRAIN_COLORS" : (1.0,0.9,0.9)  ,         # Brain color
        "MASK_COLORS" : {
            1: (1.0, 0.0, 0.0),                   # Label 1 color
            2: (1.0, 1.0, 0.0),                   # Label 2 color
            3: (0.0, 1.0, 0.0),                   # Label 3 color
            4: (0.0, 0.0, 1.0),                   # Label 4 color
            5: (0.0, 1.0, 1.0)                    # Label 5 color
        },
        "PRED_COLORS" : {
            'tp': (0.36, 0.68, 0.68) ,            # True positive color
            'fp': (0.56, 0.1, 1),                 # False positive color
            'fn': (1, 0.5, 0)                     # False negative color
        }
    }
    
    data_file = sitk.ReadImage("test_data/BraTS-MET-00001-000-t2f.nii.gz")
    data = [sitk.GetArrayFromImage(data_file), sitk.GetArrayFromImage(data_file), sitk.GetArrayFromImage(data_file)]
    # data = [sitk.GetArrayFromImage(data_file)]
    label_file = sitk.ReadImage("test_data/BraTS-MET-00001-000-seg.nii.gz")
    label = [sitk.GetArrayFromImage(label_file), None, sitk.GetArrayFromImage(label_file)]
    # label = [sitk.GetArrayFromImage(label_file)]
    app = QApplication(sys.argv)
    dlg = MultiImgSliceViewer(data, label, DEFAULT_COLORS)
    dlg.show()
    sys.exit(app.exec())