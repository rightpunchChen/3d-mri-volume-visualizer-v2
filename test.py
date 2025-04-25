import sys, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PySide6.QtWidgets import QMainWindow, QFileDialog, QProgressDialog, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# 以下工具函數與視窗請依專案架構自行調整匯入路徑
from windows.message_box import show_error_message
from utils.vtk_tools import load_image, vtk_img_to_numpy, check_files


# =============================================================================
# OrthogonalViewer：基於 matplotlib 建立三方向切片視圖，並加入 overlay actor
# =============================================================================
class OrthogonalViewer:
    def __init__(self, brain_volume, label_volume=None, pred_volume=None, colors=None):
        """
        brain_volume : numpy array (3D) 腦部影像
        label_volume : numpy array (3D) 標記影像，若存在則 overlay 到各切片
        pred_volume  : numpy array (3D) 預測影像，若存在則 overlay 到各切片
        colors       : dict，包含 MASK_COLORS 與 PRED_COLORS 之配色設定
        """
        self.brain = brain_volume
        self.label = label_volume
        self.pred = pred_volume
        self.colors = colors

        self.nx, self.ny, self.nz = self.brain.shape
        # 假設未做補零，所以 offset 為 0
        self.offset_x, self.offset_y, self.offset_z = 0, 0, 0
        self.orig_nx, self.orig_ny, self.orig_nz = self.nx, self.ny, self.nz

        # 初始 voxel 位置設為影像中心
        self.x_idx = self.orig_nx // 2
        self.y_idx = self.orig_ny // 2
        self.z_idx = self.orig_nz // 2

        # 模式設定：mouse / glove / magnifier（預設 mouse）
        self.mode = 'mouse'
        # 載入圖示（請確認檔案路徑正確）
        self.mouse_icon = plt.imread('mouse_icon.png')
        self.glove_icon = plt.imread('glove_icon.png')
        self.magnifier_icon = plt.imread('magnifier.png')
        self.magnifier_pixmap = QPixmap('magnifier_icon.png').scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 建立 2x2 子圖，使用 3 個顯示區（左下角隱藏）
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        self.axial_ax    = self.axes[0, 0]  # Axial
        self.sagittal_ax = self.axes[0, 1]  # Sagittal
        self.coronal_ax  = self.axes[1, 1]  # Coronal
        self.axes[1, 0].axis("off")         # 隱藏左下

        for ax in [self.axial_ax, self.sagittal_ax, self.coronal_ax]:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_aspect('equal')
            ax.set_facecolor('black')

        self.fig.subplots_adjust(wspace=0.05, hspace=0.1)

        # 建立 brain 影像顯示（使用灰階）
        self.axial_im = self.axial_ax.imshow(self.brain[:, :, self.z_idx].T,
                                             cmap='gray', origin='lower')
        self.axial_ax.set_title(f'Axial (z={self.z_idx+1})')
        
        self.sagittal_im = self.sagittal_ax.imshow(self.brain[self.x_idx, :, :].T,
                                                    cmap='gray', origin='lower')
        self.sagittal_ax.set_title(f'Sagittal (x={self.x_idx+1})')
        
        self.coronal_im = self.coronal_ax.imshow(self.brain[:, self.y_idx, :].T,
                                                  cmap='gray', origin='lower')
        self.coronal_ax.set_title(f'Coronal (y={self.y_idx+1})')
        
        # 在圖上加入 voxel 數值文字（置中）
        self.voxel_text = self.fig.text(0.5, 0.95, '', ha='center', va='center', fontsize=14)
        self.update_voxel_text()

        # 連結滑鼠事件
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)

        # 用來節流更新的旗標
        from PySide6.QtCore import QTimer
        self._update_pending = False

    def update_voxel_text(self):
        voxel_value = self.brain[self.x_idx, self.y_idx, self.z_idx]
        self.voxel_text.set_text(f'Voxel Value: {voxel_value:.2f}')

    def update_views(self):
        # 更新 brain 切片
        self.axial_im.set_data(self.brain[:, :, self.z_idx].T)
        self.axial_ax.set_title(f'Axial (z={self.z_idx+1})')
        
        self.sagittal_im.set_data(self.brain[self.x_idx, :, :].T)
        self.sagittal_ax.set_title(f'Sagittal (x={self.x_idx+1})')
        
        self.coronal_im.set_data(self.brain[:, self.y_idx, :].T)
        self.coronal_ax.set_title(f'Coronal (y={self.y_idx+1})')

        # 若 label 影像存在，將 overlay 加入（使用半透明效果）
        for ax in [self.axial_ax, self.sagittal_ax, self.coronal_ax]:
            # 清除除底層 brain 之外的 overlay（保留第一張影像）
            ax.images = ax.images[:1]
        if self.label is not None:
            # 這裡假設 label 為整數，且顏色設定在 colors["MASK_COLORS"] 中（1~5）
            from matplotlib.colors import ListedColormap
            if self.colors and "MASK_COLORS" in self.colors:
                mask_colors = self.colors["MASK_COLORS"]
                # 建立一個 colormap，背景以黑色表示
                cmap = ListedColormap(['black'] + [f"#{int(c[0]*255):02x}{int(c[1]*255):02x}{int(c[2]*255):02x}" for c in mask_colors.values()])
            else:
                cmap = 'jet'
            axial_label = self.label[:, :, self.z_idx].T
            sagittal_label = self.label[self.x_idx, :, :].T
            coronal_label = self.label[:, self.y_idx, :].T
            self.axial_ax.imshow(axial_label, cmap=cmap, alpha=0.5, origin='lower')
            self.sagittal_ax.imshow(sagittal_label, cmap=cmap, alpha=0.5, origin='lower')
            self.coronal_ax.imshow(coronal_label, cmap=cmap, alpha=0.5, origin='lower')
        # 若 prediction 影像存在，則 overlay 固定以 'hot' colormap
        if self.pred is not None:
            axial_pred = self.pred[:, :, self.z_idx].T
            sagittal_pred = self.pred[self.x_idx, :, :].T
            coronal_pred = self.pred[:, self.y_idx, :].T
            self.axial_ax.imshow(axial_pred, cmap='hot', alpha=0.5, origin='lower')
            self.sagittal_ax.imshow(sagittal_pred, cmap='hot', alpha=0.5, origin='lower')
            self.coronal_ax.imshow(coronal_pred, cmap='hot', alpha=0.5, origin='lower')

        self.update_voxel_text()
        self.fig.canvas.draw_idle()

    def schedule_update(self):
        from PySide6.QtCore import QTimer
        if not self._update_pending:
            self._update_pending = True
            QTimer.singleShot(30, self.perform_update)

    def perform_update(self):
        self._update_pending = False
        self.update_views()

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
        if self.mode == 'glove':
            self.fig.canvas.setCursor(QCursor(Qt.SizeAllCursor))
        elif self.mode == 'mouse':
            self.fig.canvas.setCursor(QCursor(Qt.ArrowCursor))
        elif self.mode == 'magnifier':
            self.fig.canvas.setCursor(QCursor(self.magnifier_pixmap))

        if self.mode == 'magnifier' and self.magnifier_rect is not None and self.magnifier_start is not None:
            if self.magnifier_ax is not None:
                bbox = self.magnifier_ax.get_window_extent()
                x_lim = self.magnifier_ax.get_xlim()
                y_lim = self.magnifier_ax.get_ylim()
                if event.xdata is None or event.ydata is None:
                    current_data = self.magnifier_ax.transData.inverted().transform((event.x, event.y))
                    current_xdata, current_ydata = current_data
                else:
                    current_xdata = event.xdata
                    current_ydata = event.ydata
                if event.x > bbox.x1:
                    current_xdata = x_lim[1]
                elif event.x < bbox.x0:
                    current_xdata = x_lim[0]
                if event.y > bbox.y1:
                    current_ydata = y_lim[1]
                elif event.y < bbox.y0:
                    current_ydata = y_lim[0]
                x0, y0 = self.magnifier_start
                width = current_xdata - x0
                height = current_ydata - y0
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

        if self.mode == 'mouse' and getattr(self, 'dragging', False):
            ax = self.active_ax
            if ax is None:
                return
            data_x, data_y = ax.transData.inverted().transform((event.x, event.y))
            if ax == self.axial_ax:
                new_x = int(data_x)
                new_y = int(data_y)
                self.x_idx = np.clip(new_x, 0, self.orig_nx - 1)
                self.y_idx = np.clip(new_y, 0, self.orig_ny - 1)
            elif ax == self.sagittal_ax:
                new_y = int(data_x)
                new_z = int(data_y)
                self.y_idx = np.clip(new_y, 0, self.orig_ny - 1)
                self.z_idx = np.clip(new_z, 0, self.orig_nz - 1)
            elif ax == self.coronal_ax:
                new_x = int(data_x)
                new_z = int(data_y)
                self.x_idx = np.clip(new_x, 0, self.orig_nx - 1)
                self.z_idx = np.clip(new_z, 0, self.orig_nz - 1)
            self.schedule_update()

        if self.zooming and self.zoom_ax is not None and event.y is not None:
            delta_y = event.y - self.last_zoom_y
            factor = 1.0 - delta_y / 100.0
            new_scale = self.current_scale * factor
            new_scale = np.clip(new_scale, 0.5, 2.0)
            new_half_range_x = self.base_half_range_x * new_scale
            new_half_range_y = self.base_half_range_y * new_scale
            new_xlim = (self.zoom_center_x - new_half_range_x, self.zoom_center_x + new_half_range_x)
            new_ylim = (self.zoom_center_y - new_half_range_y, self.zoom_center_y + new_half_range_y)
            self.zoom_ax.set_xlim(new_xlim)
            self.zoom_ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()
            self.current_scale = new_scale
            self.last_zoom_y = event.y

    def on_release(self, event):
        if event.button == 1:
            if self.mode == 'magnifier' and self.magnifier_rect is not None:
                x0, y0 = self.magnifier_rect.get_xy()
                width = self.magnifier_rect.get_width()
                height = self.magnifier_rect.get_height()
                if width > 0 and height > 0:
                    center_x = x0 + width / 2.0
                    center_y = y0 + height / 2.0
                    long_side = max(width, height)
                    new_xlim = (center_x - long_side / 2, center_x + long_side / 2)
                    new_ylim = (center_y - long_side / 2, center_y + long_side / 2)
                    self.magnifier_ax.set_xlim(new_xlim)
                    self.magnifier_ax.set_ylim(new_ylim)
                self.magnifier_rect.remove()
                self.magnifier_rect = None
                self.fig.canvas.draw_idle()
            else:
                self.left_pressed = False
                self.dragging = False
        elif event.button == 3:
            self.right_pressed = False
            self.zooming = False

    def on_scroll(self, event):
        ax = event.inaxes
        if ax is None:
            return
        if ax == self.axial_ax:
            if event.button == 'up':
                self.z_idx = max(0, self.z_idx - 1)
            elif event.button == 'down':
                self.z_idx = min(self.orig_nz - 1, self.z_idx + 1)
        elif ax == self.sagittal_ax:
            if event.button == 'up':
                self.x_idx = max(0, self.x_idx - 1)
            elif event.button == 'down':
                self.x_idx = min(self.orig_nx - 1, self.x_idx + 1)
        elif ax == self.coronal_ax:
            if event.button == 'up':
                self.y_idx = max(0, self.y_idx - 1)
            elif event.button == 'down':
                self.y_idx = min(self.orig_ny - 1, self.y_idx + 1)
        self.update_views()


# =============================================================================
# SliceViewerController：上方提供檔案載入與 Render 按鈕，
# 載入影像後直接利用 OrthogonalViewer 顯示三方向切片圖（內含 overlay actor）
# =============================================================================
class SliceViewerController(QMainWindow):
    def __init__(self, colors: dict):
        super().__init__()
        self.colors = colors
        self.init_ui()
        self.brain_volume = None
        self.label_volume = None
        self.pred_volume = None
        self.orthoviewer = None

    def init_ui(self):
        # 建立基本 GUI，包含上方檔案載入與 Render 按鈕
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 上方控制列
        controls_layout = QHBoxLayout()
        self.BF_btn = QPushButton("Open Brain File", self)
        self.BF_lineEdit = QLineEdit(self)
        self.LF_btn = QPushButton("Open Label File", self)
        self.LF_lineEdit = QLineEdit(self)
        self.PF_btn = QPushButton("Open Prediction File", self)
        self.PF_lineEdit = QLineEdit(self)
        self.render_pushButton = QPushButton("Render Brain", self)
        
        controls_layout.addWidget(self.BF_btn)
        controls_layout.addWidget(self.BF_lineEdit)
        controls_layout.addWidget(self.LF_btn)
        controls_layout.addWidget(self.LF_lineEdit)
        controls_layout.addWidget(self.PF_btn)
        controls_layout.addWidget(self.PF_lineEdit)
        controls_layout.addWidget(self.render_pushButton)
        
        layout.addLayout(controls_layout)
        
        # 放置 OrthogonalViewer 的區域
        self.canvas_widget = QWidget(self)
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        layout.addWidget(self.canvas_widget)
        
        # 連結訊號
        self.BF_btn.clicked.connect(self.open_brain_file)
        self.LF_btn.clicked.connect(self.open_label_file)
        self.PF_btn.clicked.connect(self.open_prediction_file)
        self.render_pushButton.clicked.connect(self.render_brain)
        self.BF_lineEdit.returnPressed.connect(self.update_render_button)
        self.LF_lineEdit.returnPressed.connect(self.update_label_button)
        self.PF_lineEdit.returnPressed.connect(self.update_pred_button)
        
    def open_brain_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.BF_lineEdit.setText(file_path)
        self.update_render_button()

    def open_label_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.LF_lineEdit.setText(file_path)
        self.update_label_button()

    def open_prediction_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.PF_lineEdit.setText(file_path)
        self.update_pred_button()

    def update_render_button(self):
        self.brain_volume = None
        file_path = self.BF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            vtk_brain = load_image(file_path)
            # 轉換成 numpy 陣列
            self.brain_volume = vtk_img_to_numpy(vtk_brain)
        else:
            show_error_message(f"File does not exist: {file_path}")

    def update_label_button(self):
        self.label_volume = None
        file_path = self.LF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            vtk_label = load_image(file_path)
            self.label_volume = vtk_img_to_numpy(vtk_label)
        else:
            show_error_message(f"File does not exist: {file_path}")

    def update_pred_button(self):
        self.pred_volume = None
        file_path = self.PF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            vtk_pred = load_image(file_path)
            self.pred_volume = vtk_img_to_numpy(vtk_pred)
        else:
            show_error_message(f"File does not exist: {file_path}")

    def render_brain(self):
        if self.brain_volume is None:
            show_error_message("Brain volume not loaded.")
            return
        # 清除先前的 viewer（若有）
        if self.orthoviewer:
            self.canvas_layout.removeWidget(self.orthoviewer_canvas)
            self.orthoviewer_canvas.setParent(None)
        # 建立 OrthogonalViewer，並傳入 brain, label 與 prediction 影像及顏色設定
        self.orthoviewer = OrthogonalViewer(self.brain_volume, self.label_volume, self.pred_volume, self.colors)
        self.orthoviewer_canvas = FigureCanvas(self.orthoviewer.fig)
        self.canvas_layout.addWidget(self.orthoviewer_canvas)
        self.orthoviewer_canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 範例顏色設定（請依需求調整）
    colors = {
        "MASK_COLORS": {
            1: (1, 0, 0),
            2: (0, 1, 0),
            3: (0, 0, 1),
            4: (1, 1, 0),
            5: (1, 0, 1),
        },
        "PRED_COLORS": {
            "tp": (0, 1, 1),
            "fp": (1, 0.5, 0),
            "fn": (0.5, 0, 1)
        }
    }
    window = SliceViewerController(colors)
    window.show()
    sys.exit(app.exec())
