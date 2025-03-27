import os
import numpy as np
import SimpleITK as sitk
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QCursor, QPixmap
from PySide6.QtWidgets import (
    QApplication, QComboBox, QLabel, QPushButton,
    QRadioButton, QSizePolicy, QSlider, QSpinBox,
    QVBoxLayout, QWidget, QFileDialog
    )
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
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

class OmnidirectionalSliceViewer(QWidget):
    def __init__(self, data, pred, colors):
        super().__init__()
        self.data, self.orig_shape = self.pad_to_cube(data)
        if pred is not None:
            self.label, _ = self.pad_to_cube(pred)
        else:
            self.label = None
        self.labeled_image = np.stack([self.normalize(self.data)] * 3, axis=-1)
        self.colors = colors

        self.init()
        self.init_fig()
        self.init_ui()

    def init(self):
        self.nx, self.ny, self.nz, _ = self.labeled_image.shape

        if self.orig_shape is None:
            self.orig_nx, self.orig_ny, self.orig_nz = self.nx, self.ny, self.nz
            self.offset_x, self.offset_y, self.offset_z = 0, 0, 0
        else:
            self.orig_nx, self.orig_ny, self.orig_nz = self.orig_shape
            self.offset_x = (self.nx - self.orig_nx) // 2
            self.offset_y = (self.ny - self.orig_ny) // 2
            self.offset_z = (self.nz - self.orig_nz) // 2

        # 初始 voxel 位置設在原始影像中心 (在補零後的座標系統中)
        self.x_idx = self.offset_x + self.orig_nx // 2
        self.y_idx = self.offset_y + self.orig_ny // 2
        self.z_idx = self.offset_z + self.orig_nz // 2

        # 操作狀態參數
        self.dragging = False
        self.zooming = False
        self.panning = False
        self.left_pressed = False
        self.right_pressed = False
        self.active_ax = None   # 拖曳用
        self.zoom_ax = None     # 縮放用
        self.zoom_center_x = None
        self.zoom_center_y = None
        self.base_half_range_x = None
        self.base_half_range_y = None
        self.current_scale = 1.0
        self.last_zoom_y = None
        self.min_zoom = 0.5  
        self.max_zoom = 2.0  

        # magnifier 模式參數
        self.magnifier_mode = False
        self.magnifier_start = None
        self.magnifier_rect = None

        # 預設模式為鼠標模式
        self.mode = 'mouse'
        
        self.mouse_icon = plt.imread(os.path.join('utils', 'fig', 'mouse_icon.png'))
        self.glove_icon = plt.imread(os.path.join('utils', 'fig','glove_icon.png'))
        self.magnifier_icon = plt.imread(os.path.join('utils', 'fig','magnifier.png'))

    def init_fig(self):
        # 建立 2x2 子圖，並隱藏左下角；設定背景為黑色
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        self.axial_ax    = self.axes[0, 0]  # 左上：Axial
        self.sagittal_ax = self.axes[0, 1]  # 右上：Sagittal
        self.coronal_ax  = self.axes[1, 1]  # 右下：Coronal
        self.axes[1, 0].axis("off")         # 隱藏左下

        # 調整錨定點：左右與上下的對齊
        self.axial_ax.set_anchor('SE')      
        self.sagittal_ax.set_anchor('SW')   
        self.coronal_ax.set_anchor('NW')    

        for ax in [self.axial_ax, self.sagittal_ax, self.coronal_ax]:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_aspect('equal')
            ax.set_facecolor('black')
        self.fig.subplots_adjust(wspace=0.05, hspace=0.1)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)

        # ----------------------------
        # Axial 視圖
        # ----------------------------
        self.axial_im = self.axial_ax.imshow(np.transpose(self.labeled_image[:, :, self.z_idx], (1, 0, 2)),
                                             cmap='gray', origin='lower')
        self.axial_ax.set_title(f'Axial (z={self.z_idx - self.offset_z + 1})')
        self.axial_vline = self.axial_ax.axvline(x=self.x_idx, color='r', linestyle='--')
        self.axial_hline = self.axial_ax.axhline(y=self.y_idx, color='r', linestyle='--')
        
        # ----------------------------
        # Sagittal 視圖
        # ----------------------------
        self.sagittal_im = self.sagittal_ax.imshow(np.transpose(self.labeled_image[self.x_idx, :, :], (1, 0, 2)),
                                                    cmap='gray', origin='lower')
        self.sagittal_ax.set_title(f'Sagittal (x={self.x_idx - self.offset_x + 1})')
        self.sagittal_vline = self.sagittal_ax.axvline(x=self.y_idx, color='r', linestyle='--')
        self.sagittal_hline = self.sagittal_ax.axhline(y=self.z_idx, color='r', linestyle='--')
        
        # ----------------------------
        # Coronal 視圖
        # ----------------------------
        self.coronal_im = self.coronal_ax.imshow(np.transpose(self.labeled_image[:, self.y_idx, :], (1, 0, 2)),
                                                  cmap='gray', origin='lower')
        self.coronal_ax.set_title(f'Coronal (y={self.y_idx - self.offset_y + 1})')
        self.coronal_vline = self.coronal_ax.axvline(x=self.x_idx, color='r', linestyle='--')
        self.coronal_hline = self.coronal_ax.axhline(y=self.z_idx, color='r', linestyle='--')
        
        # 儲存各 axes 初始顯示範圍 (用於 reset)
        self.axial_xlim0 = self.axial_ax.get_xlim()
        self.axial_ylim0 = self.axial_ax.get_ylim()
        self.sagittal_xlim0 = self.sagittal_ax.get_xlim()
        self.sagittal_ylim0 = self.sagittal_ax.get_ylim()
        self.coronal_xlim0 = self.coronal_ax.get_xlim()
        self.coronal_ylim0 = self.coronal_ax.get_ylim()
        
        # 顯示 voxel 數值的文字
        self.voxel_text = self.fig.text(0.5, 0.95, '', ha='center', va='center', fontsize=14)
        self.update_voxel_text()
        
        # 加入模式切換按鈕：mouse, glove, magnifier (使用 icon)
        mouse_ax = self.fig.add_axes([0.85, 0.80, 0.05, 0.05])
        self.mouse_button = Button(mouse_ax, '')
        mouse_ax.imshow(self.mouse_icon, aspect='equal')
        self.mouse_button.on_clicked(self.set_mouse_mode)
        
        glove_ax = self.fig.add_axes([0.85, 0.75, 0.05, 0.05])
        self.glove_button = Button(glove_ax, '')
        glove_ax.imshow(self.glove_icon, aspect='equal')
        self.glove_button.on_clicked(self.set_glove_mode)
        
        magnifier_ax = self.fig.add_axes([0.85, 0.70, 0.05, 0.05])
        self.magnifier_button = Button(magnifier_ax, '')
        magnifier_ax.imshow(self.magnifier_icon, aspect='equal')
        self.magnifier_button.on_clicked(self.set_magnifier_mode)
        
        # 連接滑鼠事件
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def init_ui(self):
        self.centralwidget = QWidget()

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.canvas = FigureCanvas(self.fig)

        self.canvas_widget = QWidget(self.centralwidget)
        self.canvas_widget.setObjectName(u"canvas_widget")
        # self.canvas_widget.setMinimumSize(1200, 800)
        self.canvas_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        self.canvas_layout.setContentsMargins(0,0,0,0)
        self.canvas_layout.addWidget(self.canvas) 

        self.panel_widget = QWidget(self.centralwidget)
        self.panel_widget.setObjectName(u"panel_widget")
        self.panel_widget.setFixedSize(491, 120)

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
        self.op_label.setGeometry(QRect(30, 40, 91, 21))
        self.op_spinBox = QSpinBox(self.panel_widget)
        self.op_spinBox.setObjectName(u"op_spinBox")
        self.op_spinBox.setGeometry(QRect(90, 40, 51, 24))
        self.op_spinBox.setMinimum(0)
        self.op_spinBox.setMaximum(40)
        self.op_spinBox.setValue(20)
        self.op_spinBox.setEnabled(False)
        self.render_pushButton = QPushButton("Render", self.panel_widget)
        self.render_pushButton.setObjectName(u"render_pushButton")
        self.render_pushButton.setGeometry(QRect(30, 80, 113, 32))

        self.main_layout.addWidget(self.canvas_widget)
        self.main_layout.addWidget(self.panel_widget)
        self.setLayout(self.main_layout)
        self.init_label_radioButton()
        self.render_pushButton.clicked.connect(self.reset_views)

    def init_label_radioButton(self):
        if self.label is None:
            return
        max_label = int(self.label.max())
        for i in range(1, min(max_label + 1, 6)):
            r = int(self.colors["MASK_COLORS"][i][0]*255)
            g = int(self.colors["MASK_COLORS"][i][1]*255)
            b = int(self.colors["MASK_COLORS"][i][2]*255)
            button = getattr(self, f'lab_radioButton_{i}')
            button.setStyleSheet(f"color: rgb({r}, {g}, {b});")
            button.setEnabled(True)

    def pad_to_cube(self, data):
        """
        將影像補零使其變成正立方體
        回傳 (padded_volume, orig_shape)
        """
        nx, ny, nz = data.shape
        cube_dim = max(nx, ny, nz)
        pad_x_before = (cube_dim - nx) // 2
        pad_y_before = (cube_dim - ny) // 2
        pad_z_before = (cube_dim - nz) // 2
        pad_x_after = cube_dim - nx - pad_x_before
        pad_y_after = cube_dim - ny - pad_y_before
        pad_z_after = cube_dim - nz - pad_z_before
        padded_volume = np.pad(data, 
                            ((pad_x_before, pad_x_after),
                                (pad_y_before, pad_y_after),
                                (pad_z_before, pad_z_after)),
                            mode='constant', constant_values=0)
        return padded_volume, (nx, ny, nz)
    
    def update_voxel_text(self):
        voxel_value = self.data[self.x_idx, self.y_idx, self.z_idx]
        self.voxel_text.set_text(f'Voxel Value: {voxel_value:.2f}')
    
    def update_views(self):
        self.axial_im.set_data(np.transpose(self.labeled_image[:, :, self.z_idx], (1, 0, 2)))
        self.axial_ax.set_title(f'Axial (z={self.z_idx - self.offset_z + 1})')
        self.axial_vline.set_xdata([self.x_idx, self.x_idx])
        self.axial_hline.set_ydata([self.y_idx, self.y_idx])
        
        self.sagittal_im.set_data(np.transpose(self.labeled_image[self.x_idx, :, :], (1, 0, 2)))
        self.sagittal_ax.set_title(f'Sagittal (x={self.x_idx - self.offset_x + 1})')
        self.sagittal_vline.set_xdata([self.y_idx, self.y_idx])
        self.sagittal_hline.set_ydata([self.z_idx, self.z_idx])
        
        self.coronal_im.set_data(np.transpose(self.labeled_image[:, self.y_idx, :], (1, 0, 2)))
        self.coronal_ax.set_title(f'Coronal (y={self.y_idx - self.offset_y + 1})')
        self.coronal_vline.set_xdata([self.x_idx, self.x_idx])
        self.coronal_hline.set_ydata([self.z_idx, self.z_idx])
        
        self.update_voxel_text()
        self.fig.canvas.draw_idle()

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
    
    def reset_views(self):
        selected_label = []
        for i in range(1, 6):
            radio_button = getattr(self, f'lab_radioButton_{i}')
            if radio_button.isChecked():
                selected_label.append(i)
        if len(selected_label) != 0:
            self.op_spinBox.setEnabled(True)
        else:
            self.op_spinBox.setEnabled(False)

        if self.label is not None:
            self.labeled_image = self.labeled_img(
                    self.data,
                    self.label,
                    label_value=selected_label,
                    alpha=self.op_spinBox.value() / 100)
    
        self.axial_ax.set_xlim(self.axial_xlim0)
        self.axial_ax.set_ylim(self.axial_ylim0)
        self.sagittal_ax.set_xlim(self.sagittal_xlim0)
        self.sagittal_ax.set_ylim(self.sagittal_ylim0)
        self.coronal_ax.set_xlim(self.coronal_xlim0)
        self.coronal_ax.set_ylim(self.coronal_ylim0)
        self.zooming = False
        self.panning = False
        self.current_scale = 1.0
        self.update_views()

    def set_mouse_mode(self, event):
        self.mode = 'mouse'
        self.fig.canvas.setCursor(QCursor(Qt.ArrowCursor))
        # print("切換到鼠標模式")

    def set_glove_mode(self, event):
        self.mode = 'glove'
        self.fig.canvas.setCursor(QCursor(Qt.SizeAllCursor))
        # print("切換到手套模式")
    
    def set_magnifier_mode(self, event):
        self.mode = 'magnifier'
        self.magnifier_pixmap = QPixmap('magnifier_icon.png').scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.fig.canvas.setCursor(QCursor(self.magnifier_pixmap))
        # print("切換到放大鏡模式")
    
    def start_pan(self, event):
        self.panning = True
        self.pan_ax = event.inaxes
        self.pan_start_disp = (event.x, event.y)
        self.pan_start_data = (event.xdata, event.ydata)
        self.pan_orig_xlim = self.pan_ax.get_xlim()
        self.pan_orig_ylim = self.pan_ax.get_ylim()

    def on_press(self, event):
        if event.inaxes not in [self.axial_ax, self.sagittal_ax, self.coronal_ax]:
            return
        
        if self.mode == 'mouse':
            if event.button == 1:
                self.left_pressed = True
                self.dragging = True
                self.active_ax = event.inaxes
                self.on_motion(event)
            elif event.button == 3:
                self.right_pressed = True
                self.zooming = True
                self.zoom_ax = event.inaxes
                self.zoom_initial_xlim = self.zoom_ax.get_xlim()
                self.zoom_initial_ylim = self.zoom_ax.get_ylim()
                self.zoom_center_x = (self.zoom_initial_xlim[0] + self.zoom_initial_xlim[1]) / 2.0
                self.zoom_center_y = (self.zoom_initial_ylim[0] + self.zoom_initial_ylim[1]) / 2.0
                self.base_half_range_x = (self.zoom_initial_xlim[1] - self.zoom_initial_xlim[0]) / 2.0
                self.base_half_range_y = (self.zoom_initial_ylim[1] - self.zoom_initial_ylim[0]) / 2.0
                self.current_scale = 1.0
                self.last_zoom_y = event.y
        elif self.mode == 'glove':
            if event.button == 1:
                self.left_pressed = True
                self.start_pan(event)
            elif event.button == 3:
                self.right_pressed = True
                self.zooming = True
                self.zoom_ax = event.inaxes
                self.zoom_initial_xlim = self.zoom_ax.get_xlim()
                self.zoom_initial_ylim = self.zoom_ax.get_ylim()
                self.zoom_center_x = (self.zoom_initial_xlim[0] + self.zoom_initial_xlim[1]) / 2.0
                self.zoom_center_y = (self.zoom_initial_ylim[0] + self.zoom_initial_ylim[1]) / 2.0
                self.base_half_range_x = (self.zoom_initial_xlim[1] - self.zoom_initial_xlim[0]) / 2.0
                self.base_half_range_y = (self.zoom_initial_ylim[1] - self.zoom_initial_ylim[0]) / 2.0
                self.current_scale = 1.0
                self.last_zoom_y = event.y
        elif self.mode == 'magnifier':
            if event.button == 1:
                # 記錄放大鏡的起點，並在當前軸上新增矩形 patch
                self.magnifier_start = (event.xdata, event.ydata)
                self.magnifier_ax = event.inaxes
                self.magnifier_rect = Rectangle((event.xdata, event.ydata), 0, 0,
                                                edgecolor='yellow', facecolor='none', linestyle='--')
                self.magnifier_ax.add_patch(self.magnifier_rect)
                self.fig.canvas.draw_idle()
            elif event.button == 3:
                self.right_pressed = True
                self.zooming = True
                self.zoom_ax = event.inaxes
                self.zoom_initial_xlim = self.zoom_ax.get_xlim()
                self.zoom_initial_ylim = self.zoom_ax.get_ylim()
                self.zoom_center_x = (self.zoom_initial_xlim[0] + self.zoom_initial_xlim[1]) / 2.0
                self.zoom_center_y = (self.zoom_initial_ylim[0] + self.zoom_initial_ylim[1]) / 2.0
                self.base_half_range_x = (self.zoom_initial_xlim[1] - self.zoom_initial_xlim[0]) / 2.0
                self.base_half_range_y = (self.zoom_initial_ylim[1] - self.zoom_initial_ylim[0]) / 2.0
                self.current_scale = 1.0
                self.last_zoom_y = event.y

    def on_motion(self, event):
        # 更新 cursor
        if self.mode == 'glove':
            self.fig.canvas.setCursor(QCursor(Qt.SizeAllCursor))
        elif self.mode == 'mouse':
            self.fig.canvas.setCursor(QCursor(Qt.ArrowCursor))
        elif self.mode == 'magnifier':
            self.fig.canvas.setCursor(QCursor(self.magnifier_pixmap))
        
        # magnifier 模式：左鍵拖曳更新矩形，並夾取在該軸邊界內
        if self.mode == 'magnifier' and self.magnifier_rect is not None and self.magnifier_start is not None:
            if self.magnifier_ax is not None:
                # 取得當前軸的 display bounding box（以像素為單位）
                bbox = self.magnifier_ax.get_window_extent()
                # 取得軸內的 data 範圍
                x_lim = self.magnifier_ax.get_xlim()
                y_lim = self.magnifier_ax.get_ylim()
                # 嘗試取得 event 的 data 座標；若為 None則用轉換值
                if event.xdata is None or event.ydata is None:
                    current_data = self.magnifier_ax.transData.inverted().transform((event.x, event.y))
                    current_xdata, current_ydata = current_data
                else:
                    current_xdata = event.xdata
                    current_ydata = event.ydata

                # 檢查 event 的 display 座標（event.x, event.y）與 bbox 比較，
                # 若超出右邊界，則以 x_lim[1] 作為目前 data x 座標，
                # 若超出左邊界，則以 x_lim[0]；對 y 軸同理
                if event.x > bbox.x1:
                    current_xdata = x_lim[1]
                elif event.x < bbox.x0:
                    current_xdata = x_lim[0]
                if event.y > bbox.y1:
                    current_ydata = y_lim[1]
                elif event.y < bbox.y0:
                    current_ydata = y_lim[0]

                # 接下來以 magnifier 起點與目前 data 座標計算矩形
                x0, y0 = self.magnifier_start
                width = current_xdata - x0
                height = current_ydata - y0
                # 如果拖曳方向為負，則調整起點
                if width < 0:
                    x0 = current_xdata
                    width = abs(width)
                if height < 0:
                    y0 = current_ydata
                    height = abs(height)
                self.magnifier_rect.set_xy((x0, y0))
                self.magnifier_rect.set_width(width)
                self.magnifier_rect.set_height(height)
                self.fig.canvas.draw_idle()
                return
        
        # mouse 模式：左鍵拖曳更新 voxel 位置
        if self.mode == 'mouse' and self.dragging:
            ax = self.active_ax
            if ax is None:
                return
            data_x, data_y = ax.transData.inverted().transform((event.x, event.y))
            if ax == self.axial_ax:
                new_x = int(data_x)
                new_y = int(data_y)
                self.x_idx = np.clip(new_x, self.offset_x, self.offset_x + self.orig_nx - 1)
                self.y_idx = np.clip(new_y, self.offset_y, self.offset_y + self.orig_ny - 1)
            elif ax == self.sagittal_ax:
                new_y = int(data_x)
                new_z = int(data_y)
                self.y_idx = np.clip(new_y, self.offset_y, self.offset_y + self.orig_ny - 1)
                self.z_idx = np.clip(new_z, self.offset_z, self.offset_z + self.orig_nz - 1)
            elif ax == self.coronal_ax:
                new_x = int(data_x)
                new_z = int(data_y)
                self.x_idx = np.clip(new_x, self.offset_x, self.offset_x + self.orig_nx - 1)
                self.z_idx = np.clip(new_z, self.offset_z, self.offset_z + self.orig_nz - 1)
            self.update_views()
        
        # 處理右鍵縮放
        if self.zooming and self.zoom_ax is not None and event.y is not None:
            delta_y = event.y - self.last_zoom_y
            factor = 1.0 - delta_y / 100.0
            new_scale = self.current_scale * factor
            new_scale = np.clip(new_scale, self.min_zoom, self.max_zoom)
            new_half_range_x = self.base_half_range_x * new_scale
            new_half_range_y = self.base_half_range_y * new_scale
            new_xlim = (self.zoom_center_x - new_half_range_x, self.zoom_center_x + new_half_range_x)
            new_ylim = (self.zoom_center_y - new_half_range_y, self.zoom_center_y + new_half_range_y)
            self.zoom_ax.set_xlim(new_xlim)
            self.zoom_ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()
            self.current_scale = new_scale
            self.last_zoom_y = event.y

        # 平移 (glove 模式)
        if self.panning and hasattr(self, 'pan_ax') and self.pan_ax is not None and event.x is not None and event.y is not None:
            current_disp = np.array([event.x, event.y])
            start_disp = np.array(self.pan_start_disp)
            delta_disp = current_disp - start_disp
            inv = self.pan_ax.transData.inverted()
            start_data_disp = np.array(self.pan_ax.transData.transform(self.pan_start_data))
            current_data_disp = start_data_disp + delta_disp
            new_data = inv.transform(current_data_disp)
            dx = new_data[0] - self.pan_start_data[0]
            dy = new_data[1] - self.pan_start_data[1]
            new_xlim = (self.pan_orig_xlim[0] - dx, self.pan_orig_xlim[1] - dx)
            new_ylim = (self.pan_orig_ylim[0] - dy, self.pan_orig_ylim[1] - dy)
            self.pan_ax.set_xlim(new_xlim)
            self.pan_ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()
            return

    def on_release(self, event):
        if event.button == 1:
            if self.mode == 'magnifier' and self.magnifier_rect is not None:
                # 取得選取的矩形範圍
                x0, y0 = self.magnifier_rect.get_xy()
                width = self.magnifier_rect.get_width()
                height = self.magnifier_rect.get_height()
                if width > 0 and height > 0:
                    center_x = x0 + width / 2.0
                    center_y = y0 + height / 2.0
                    long_side = max(width, height)
                    new_xlim = (center_x - long_side/2, center_x + long_side/2)
                    new_ylim = (center_y - long_side/2, center_y + long_side/2)
                    self.magnifier_ax.set_xlim(new_xlim)
                    self.magnifier_ax.set_ylim(new_ylim)
                self.magnifier_rect.remove()
                self.magnifier_rect = None
                self.magnifier_start = None
                self.fig.canvas.draw_idle()
            else:
                self.left_pressed = False
                self.dragging = False
        elif event.button == 3:
            self.right_pressed = False
            self.zooming = False
        if not (self.left_pressed or self.right_pressed):
            self.panning = False
            if hasattr(self, 'pan_ax'):
                self.pan_ax = None
                self.pan_start = None
                self.pan_orig_xlim = None
                self.pan_orig_ylim = None

    def on_scroll(self, event):
        ax = event.inaxes
        if ax is None:
            return

        if ax == self.axial_ax:
            if event.button == 'up':
                self.z_idx = max(self.offset_z, self.z_idx - 1)
            elif event.button == 'down':
                self.z_idx = min(self.offset_z + self.orig_nz - 1, self.z_idx + 1)
        elif ax == self.sagittal_ax:
            if event.button == 'up':
                self.x_idx = max(self.offset_x, self.x_idx - 1)
            elif event.button == 'down':
                self.x_idx = min(self.offset_x + self.orig_nx - 1, self.x_idx + 1)
        elif ax == self.coronal_ax:
            if event.button == 'up':
                self.y_idx = max(self.offset_y, self.y_idx - 1)
            elif event.button == 'down':
                self.y_idx = min(self.offset_y + self.orig_ny - 1, self.y_idx + 1)

        self.update_views()

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