import SimpleITK as sitk
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog
    )

from windows.multi_slice_viewer_window import *
from windows.message_box import show_error_message
from utils.slice_viewer_util import MultiImgSliceViewer, OmnidirectionalSliceViewer
from utils.vtk_tools import *

class RenderWorker(QObject):
    finished = Signal()
    data_ready = Signal(list, list, dict)

    def __init__(self, image_list, label_list, colors):
        super().__init__()
        self.image_list = image_list
        self.label_list = label_list
        self.colors = colors

    def process(self):
        self.data_ready.emit(self.image_list, self.label_list, self.colors)
        self.finished.emit()

class MultiSliceViewerController(QMainWindow):
    def __init__(
            self,
            msvw: MultiSliceViewer_Window,
            colors: dict
            ):
        super().__init__()
        self.msvw = msvw
        self.colors = colors
        self.image_data = [None] * 4
        self.pred_data = [None] * 4
        self.threads = []
        self.workers = []
        self.viewers = []
        self.init()

    def init(self):
        for i in range(1, 5):
            data_btn = getattr(self.msvw, f'viewer_data{i}_btn')
            data_btn.clicked.connect(lambda checked, idx=i: self.open_file_data(idx))
            pred_btn = getattr(self.msvw, f'viewer_pred{i}_btn')
            pred_btn.clicked.connect(lambda checked, idx=i: self.open_pred_data(idx))
            data_lineEdit = getattr(self.msvw, f'viewer_data{i}_lineEdit')
            data_lineEdit.textDropped.connect(lambda checked, idx=i: self.prepare_data(idx))
            data_lineEdit.returnPressed.connect(lambda checked, idx=i: self.prepare_data(idx))
            pred_lineEdit = getattr(self.msvw, f'viewer_pred{i}_lineEdit')
            pred_lineEdit.textDropped.connect(lambda checked, idx=i: self.prepare_pred(idx))
            pred_lineEdit.returnPressed.connect(lambda checked, idx=i: self.prepare_pred(idx))

        self.msvw.render_btn.clicked.connect(self.render)
        self.msvw.clear_btn.clicked.connect(self.clear_all)

    def open_file_data(self, idx):
        data_file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        lineEdit = getattr(self.msvw, f'viewer_data{idx}_lineEdit')                
        lineEdit.setText(data_file_path)
        self.prepare_data(idx)

    def prepare_data(self, idx):
        lineEdit = getattr(self.msvw, f'viewer_data{idx}_lineEdit')                
        data_file_path = lineEdit.text()
        file_exists = check_files(data_file_path)
        if file_exists:
            pred_btn = getattr(self.msvw, f'viewer_pred{idx}_btn')
            pred_btn.setEnabled(True)
            pred_lineEdit = getattr(self.msvw, f'viewer_pred{idx}_lineEdit')
            pred_lineEdit.setText("")
            pred_lineEdit.setEnabled(True)
            self.pred_data[idx-1] = None

            img = sitk.ReadImage(data_file_path)
            self.image_data[idx-1] = sitk.GetArrayFromImage(img)
            self.update_render_button()
            return
        elif data_file_path and not file_exists:
            show_error_message(f"File does not exist: {data_file_path}")

        pred_btn = getattr(self.msvw, f'viewer_pred{idx}_btn')
        pred_btn.setEnabled(False)
        pred_lineEdit = getattr(self.msvw, f'viewer_pred{idx}_lineEdit')
        pred_lineEdit.setEnabled(False)
        pred_lineEdit.setText("")
        self.image_data[idx-1] = None
        self.pred_data[idx-1] = None
        self.update_render_button()

    def open_pred_data(self, idx):
        data_file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        lineEdit = getattr(self.msvw, f'viewer_pred{idx}_lineEdit')                
        lineEdit.setText(data_file_path)
        self.prepare_pred(idx)
        

    def prepare_pred(self, idx):
        lineEdit = getattr(self.msvw, f'viewer_pred{idx}_lineEdit')                
        data_file_path = lineEdit.text()
        file_exists = check_files(data_file_path)
        if file_exists:
            img = sitk.ReadImage(data_file_path)
            self.pred_data[idx-1] = sitk.GetArrayFromImage(img)
            return
        elif data_file_path and not file_exists:
            show_error_message(f"File does not exist: {data_file_path}")
        self.pred_data[idx-1] = None

    def update_render_button(self):
        for i in range(len(self.image_data)):
            if self.image_data[i] is not None :
                self.msvw.render_btn.setEnabled(True)
                break
            else :
                self.msvw.render_btn.setEnabled(False)
    
    def render(self):
        image_list = []
        label_list = []
        for idx, img in enumerate(self.image_data):
            if img is None: continue
            image_list.append(img)
            label_list.append(self.pred_data[idx])

        render_thread = QThread()
        render_worker = RenderWorker(image_list, label_list, self.colors)

        render_worker.moveToThread(render_thread)
        render_thread.started.connect(render_worker.process)
        render_worker.data_ready.connect(self.create_viewer)
        render_worker.finished.connect(render_thread.quit)
        render_worker.finished.connect(render_worker.deleteLater)
        render_thread.finished.connect(render_thread.deleteLater)

        self.threads.append(render_thread)
        self.workers.append(render_worker)

        render_thread.start()
    
    def create_viewer(self, image_list, label_list, colors):
        viewer = MultiImgSliceViewer(image_list, label_list, colors)
        viewer.show()
        self.viewers.append(viewer)

    def clear_all (self):
        for i in range(1, 5):
            pred_btn = getattr(self.msvw, f'viewer_pred{i}_btn')
            pred_btn.setEnabled(False)
            data_lineEdit = getattr(self.msvw, f'viewer_data{i}_lineEdit')
            data_lineEdit.setText("")
            pred_lineEdit = getattr(self.msvw, f'viewer_pred{i}_lineEdit')
            pred_lineEdit.setText("")

        self.image_data = [None] * 4
        self.pred_data = [None] * 4

        self.update_render_button()


class OmnidirectionalViewerController(QMainWindow):
    def __init__(
            self,
            ovw: OmnidirectionalViewer_Window,
            colors: dict
            ):
        super().__init__()
        self.ovw = ovw
        self.colors = colors
        self.image_data = None
        self.pred_data = None
        self.threads = []
        self.workers = []
        self.viewers = []
        self.init()

    def init(self):
        self.ovw.viewer_data_btn.clicked.connect(self.open_file_data)
        self.ovw.viewer_pred_btn.clicked.connect(self.open_pred_data)
       
        self.ovw.viewer_data_lineEdit.textDropped.connect(self.prepare_data)
        self.ovw.viewer_data_lineEdit.returnPressed.connect(self.prepare_data)
        self.ovw.viewer_pred_lineEdit.textDropped.connect(self.prepare_pred)
        self.ovw.viewer_pred_lineEdit.returnPressed.connect(self.prepare_pred)

        self.ovw.render_btn.clicked.connect(self.render)
        self.ovw.clear_btn.clicked.connect(self.clear_all)

    def open_file_data(self):
        data_file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")            
        self.ovw.viewer_data_lineEdit.setText(data_file_path)
        self.prepare_data()

    def prepare_data(self):             
        data_file_path = self.ovw.viewer_data_lineEdit.text()
        file_exists = check_files(data_file_path)
        if file_exists:
            self.ovw.viewer_pred_btn.setEnabled(True)
            self.ovw.viewer_pred_lineEdit.setText("")
            self.ovw.viewer_pred_lineEdit.setEnabled(True)
            self.pred_data = None

            img = sitk.ReadImage(data_file_path)
            self.image_data = sitk.GetArrayFromImage(img)
            self.update_render_button()
            return
        elif data_file_path and not file_exists:
            show_error_message(f"File does not exist: {data_file_path}")

        self.ovw.viewer_pred_btn.setEnabled(False)
        self.ovw.viewer_pred_lineEdit.setEnabled(False)
        self.ovw.viewer_pred_lineEdit.setText("")
        self.image_data = None
        self.pred_data = None
        self.update_render_button()
    
    def open_pred_data(self):
        data_file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.ovw.viewer_pred_lineEdit.setText(data_file_path)
        self.prepare_pred()
        

    def prepare_pred(self):               
        data_file_path = self.ovw.viewer_pred_lineEdit.text()
        file_exists = check_files(data_file_path)
        if file_exists:
            img = sitk.ReadImage(data_file_path)
            self.pred_data = sitk.GetArrayFromImage(img)
            return
        elif data_file_path and not file_exists:
            show_error_message(f"File does not exist: {data_file_path}")
        self.pred_data = None

    def update_render_button(self):
        if self.image_data is not None :
            self.ovw.render_btn.setEnabled(True)
        else :
            self.ovw.render_btn.setEnabled(False)

    def render(self):
        render_thread = QThread()
        render_worker = RenderWorker([self.image_data], [self.pred_data], self.colors)

        render_worker.moveToThread(render_thread)
        render_thread.started.connect(render_worker.process)
        render_worker.data_ready.connect(self.create_viewer)
        render_worker.finished.connect(render_thread.quit)
        render_worker.finished.connect(render_worker.deleteLater)
        render_thread.finished.connect(render_thread.deleteLater)

        self.threads.append(render_thread)
        self.workers.append(render_worker)

        render_thread.start()

    def create_viewer(self, data, pred, colors):
        data = np.array(data[0]).T
        if pred[0] is not None:
            pred = np.array(pred[0]).T
        else:
            pred = None
        viewer = OmnidirectionalSliceViewer(data, pred, colors)
        viewer.show()
        self.viewers.append(viewer)

    def clear_all (self):
        self.ovw.viewer_pred_btn.setEnabled(False)
        self.ovw.viewer_data_lineEdit.setText("")
        self.ovw.viewer_pred_lineEdit.setText("")

        self.image_data = None
        self.pred_data = None

        self.update_render_button()