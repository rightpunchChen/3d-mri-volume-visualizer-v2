import vtk
import imageio
from vtkmodules.util import numpy_support as vtkutil
from PySide6.QtWidgets import QMainWindow, QFileDialog, QProgressDialog, QApplication

from windows.render_window import Render_Window
from windows.message_box import show_error_message
from utils.vtk_tools import *

class RenderController(QMainWindow):
    def __init__(
            self,
            rw: Render_Window,
            vtk_renderer: vtk.vtkRenderer,
            vtk_render_window: vtk.vtkRenderWindow,
            colors: dict
            ):
        super().__init__()
        self.rw = rw
        self.vtk_renderer = vtk_renderer
        self.vtk_render_window = vtk_render_window
        self.colors = colors
        self.init()
        self.init_actor()
        
        self.brain_image_vtk = None
        self.label_image = None
        self.label_image_vtk = None
        self.pred_image_vtk = None

    def init_actor(self):
        self.brain_actor = None
        self.label_actor = None
        self.tp_actor = None
        self.fp_actor = None
        self.fn_actor = None
        self.interactor = self.vtk_render_window.GetInteractor()
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(interactor_style)
        self.interactor.Initialize()

    def init(self):
        self.rw.BF_btn.clicked.connect(self.open_brain_file) 
        self.rw.LF_btn.clicked.connect(self.open_label_file)
        self.rw.PF_btn.clicked.connect(self.open_prediction_file)

        self.rw.BO_spinBox.valueChanged.connect(self.set_brain_opacity)
        self.rw.LO_spinBox.valueChanged.connect(self.set_label_opacity)
        self.rw.PO_spinBox.valueChanged.connect(self.set_pred_opacity)
        self.rw.render_pushButton.clicked.connect(self.render_brain)
        self.rw.save_pushButton.clicked.connect(self.save_mp4)

        self.rw.BF_lineEdit.textDropped.connect(self.update_render_button)
        self.rw.LF_lineEdit.textDropped.connect(self.update_label_button)
        self.rw.PF_lineEdit.textDropped.connect(self.update_pred_button)
        self.rw.LF_lineEdit.returnPressed.connect(self.update_label_button)
        self.rw.BF_lineEdit.returnPressed.connect(self.update_render_button)
        self.rw.PF_lineEdit.returnPressed.connect(self.update_pred_button)

    def open_brain_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.rw.BF_lineEdit.setText(file_path)
        self.update_render_button()
    
    def open_label_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.rw.LF_lineEdit.setText(file_path)
        self.update_label_button()
        
    def open_prediction_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.rw.PF_lineEdit.setText(file_path)
        self.update_pred_button()

    def update_render_button(self):
        self.brain_image_vtk = None
        file_path = self.rw.BF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            self.brain_image_vtk = load_image(file_path)
            self.rw.LF_btn.setEnabled(True)
            self.rw.LF_lineEdit.setEnabled(True)
            self.rw.render_pushButton.setEnabled(True)
            return
        elif file_path and not file_exists:
            show_error_message(f"File does not exist: {file_path}")

        self.rw.LF_btn.setEnabled(False)
        self.rw.LF_lineEdit.setEnabled(False)
        self.rw.render_pushButton.setEnabled(False)
        self.rw.BO_spinBox.setEnabled(False)
        self.rw.save_pushButton.setEnabled(False)

    def update_label_button(self):
        self.label_image_vtk = None
        self.label_image = None

        file_path = self.rw.LF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            self.label_image_vtk = load_image(file_path)
            self.label_image = vtk_img_to_numpy(self.label_image_vtk)
            max_label_value = self.label_image.max()
            for i in range(1, 6):
                button = getattr(self.rw, f'radioButton_{i}')
                button.setStyleSheet("")
                button.setEnabled(False)
            for i in range(1, min(int(max_label_value) + 1, 6)):
                r = int(self.colors["MASK_COLORS"][i][0]*255)
                g = int(self.colors["MASK_COLORS"][i][1]*255)
                b = int(self.colors["MASK_COLORS"][i][2]*255)
                button = getattr(self.rw, f'radioButton_{i}')
                button.setStyleSheet(f"color: rgb({r}, {g}, {b});")
                button.setEnabled(True)
            self.rw.PF_btn.setEnabled(True)
            self.rw.PF_lineEdit.setEnabled(True)
            return
        elif file_path and not file_exists:
            show_error_message(f"File does not exist: {file_path}")

        for i in range(1, 6):
            button = getattr(self.rw, f'radioButton_{i}')
            button.setStyleSheet("")
            button.setEnabled(False)

        self.rw.LO_spinBox.setEnabled(False)
        self.rw.PF_btn.setEnabled(False)
        self.rw.PF_lineEdit.setEnabled(False)
    
    def update_pred_button(self):
        self.pred_image_vtk = None

        file_path = self.rw.PF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            self.pred_image_vtk = load_image(file_path)
            for p in ['tp', 'fp', 'fn']:
                r = int(self.colors["PRED_COLORS"][p][0]*255)
                g = int(self.colors["PRED_COLORS"][p][1]*255)
                b = int(self.colors["PRED_COLORS"][p][2]*255)
                button = getattr(self.rw, f'radioButton_{p}')
                button.setStyleSheet(f"color: rgb({r}, {g}, {b});")
                button.setEnabled(True)
            return
        elif file_path and not file_exists:
            show_error_message(f"File does not exist: {file_path}")

        for p in ['tp', 'fp', 'fn']:
            button = getattr(self.rw, f'radioButton_{p}')
            button.setStyleSheet("")
            button.setEnabled(False)

    def updata_LO_spinBox(self):
        for i in range(1, 6):
            radio_button = getattr(self.rw, f'radioButton_{i}')
            if radio_button.isChecked() and check_files(self.rw.LF_lineEdit.text()):
                self.rw.LO_spinBox.setEnabled(True)
                return
        self.rw.LO_spinBox.setEnabled(False)
        return
        
    def updata_PO_spinBox(self):
        for i in ['tp', 'fp', 'fn']:
            radio_button = getattr(self.rw, f'radioButton_{i}')
            if radio_button.isChecked() and check_files(self.rw.PF_lineEdit.text()):
                self.rw.PO_spinBox.setEnabled(True)
                return
        self.rw.PO_spinBox.setEnabled(False)
        return

    def render_brain(self):
        self.init_actor()
        self.vtk_renderer.RemoveAllViewProps()
        self.rw.BO_spinBox.setEnabled(True)
        self.rw.save_pushButton.setEnabled(True)

        self.brain_actor = setup_actor(
            self.brain_image_vtk,
            self.rw.BO_spinBox.value() / 200,
            self.colors["BRAIN_COLORS"]
            )
        self.vtk_renderer.AddActor(self.brain_actor)

        if self.label_image is not None:
            self.updata_LO_spinBox()
            selected_label = []
            for i in range(1, 6):
                radio_button = getattr(self.rw, f'radioButton_{i}')
                if radio_button.isChecked():
                    selected_label.append(i)
            if selected_label:
                self.label_actor = [None] * (max(selected_label) + 1)
                for l in range(len(selected_label)):
                    if(check_label(self.label_image, selected_label[l])): continue
                    self.label_actor[selected_label[l]] = setup_actor(
                        self.label_image_vtk,
                        self.rw.LO_spinBox.value() / 100,
                        self.colors["MASK_COLORS"][selected_label[l]],
                        selected_label[l]
                        )
                    self.vtk_renderer.AddActor(self.label_actor[selected_label[l]])
        
        if self.pred_image_vtk is not None:
            self.updata_PO_spinBox()
            if self.rw.radioButton_tp.isChecked():
                tp = AND(self.label_image_vtk, self.pred_image_vtk)
                if tp is not None:
                    self.tp_actor = setup_actor(
                        tp,
                        self.rw.PO_spinBox.value() / 100,
                        self.colors["PRED_COLORS"]['tp']
                        )
                    self.vtk_renderer.AddActor(self.tp_actor)
                    self.rw.PO_spinBox.setEnabled(True)
            if self.rw.radioButton_fp.isChecked():
                fp = false_positive(self.label_image_vtk, self.pred_image_vtk)
                if fp is not None:
                    self.fp_actor = setup_actor(
                        fp,
                        self.rw.PO_spinBox.value()/100,
                        self.colors["PRED_COLORS"]['fp']
                        )
                    self.vtk_renderer.AddActor(self.fp_actor)
                    self.rw.PO_spinBox.setEnabled(True)
            if self.rw.radioButton_fn.isChecked():
                fn = false_negative(self.label_image_vtk, self.pred_image_vtk)
                if fn is not None:
                    self.fn_actor = setup_actor(
                        fn,
                        self.rw.PO_spinBox.value()/100,
                        self.colors["PRED_COLORS"]['fn']
                        )
                    self.vtk_renderer.AddActor(self.fn_actor)
                    self.rw.PO_spinBox.setEnabled(True)
        
        set_camera(self.vtk_renderer)
        self.vtk_render_window.Render()
    
    def set_brain_opacity(self):
        opacity = self.rw.BO_spinBox.value()
        self.brain_actor.GetProperty().SetOpacity(opacity / 200)
        self.vtk_render_window.Render()
    
    def set_label_opacity(self):
        opacity = self.rw.LO_spinBox.value()
        for i in range(len(self.label_actor)):
            if self.label_actor[i] is not None:
                self.label_actor[i].GetProperty().SetOpacity(opacity / 100)
        self.vtk_render_window.Render()

    def set_pred_opacity(self):
        opacity = self.rw.PO_spinBox.value()
        if self.tp_actor is not None:
            self.tp_actor.GetProperty().SetOpacity(opacity / 100)
        if self.fp_actor is not None:
            self.fp_actor.GetProperty().SetOpacity(opacity / 100)
        if self.fn_actor is not None:
            self.fn_actor.GetProperty().SetOpacity(opacity / 100)
        self.vtk_render_window.Render()

    def save_mp4(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save MP4 file", "", "MP4 Files (*.mp4)")
        if file_path:
            if not file_path.endswith(('.mp4')):
                file_path = file_path + '.mp4'

            try:
                self.rw.save_pushButton.setEnabled(False)

                progress_dialog = QProgressDialog("Saving MP4 ... 0%", "Cancel", 0, 360, self)
                progress_dialog.setWindowTitle("Saving Progress")
                progress_dialog.setMinimumDuration(0)
                progress_dialog.show()

                window_to_image_filter = vtk.vtkWindowToImageFilter()
                window_to_image_filter.SetInput(self.vtk_render_window)
                window_to_image_filter.SetInputBufferTypeToRGB()
                window_to_image_filter.ReadFrontBufferOff()
                window_to_image_filter.SetScale(1)

                self.vtk_render_window.SetOffScreenRendering(1)
                self.vtk_render_window.SetSize(1920, 1080)
                set_camera(self.vtk_renderer)
                self.vtk_render_window.Render()
                
                writer = imageio.get_writer(file_path, fps=30, codec="libx264")
                for i in range(360):
                    self.vtk_renderer.GetActiveCamera().Azimuth(1)
                    self.vtk_render_window.Render()
                    window_to_image_filter.Modified()
                    window_to_image_filter.Update()

                    image_data = window_to_image_filter.GetOutput()
                    width, height, _ = image_data.GetDimensions()
                    frame = vtkutil.vtk_to_numpy(image_data.GetPointData().GetScalars())
                    frame = frame.reshape(height, width, -1)
                    frame = frame[::-1]

                    writer.append_data(frame)

                    progress_dialog.setValue(i)
                    progress_dialog.setLabelText(f"Saving MP4... {int((i + 1) / 360 * 100)}%")
                    QApplication.processEvents()
                    if progress_dialog.wasCanceled():
                        raise Exception("Canceled saving.")

                writer.close()
                progress_dialog.setValue(360)

            except Exception as e:
                if os.path.exists(file_path):  
                    os.remove(file_path)
                progress_dialog.setValue(360)
                show_error_message(f"Error saving MP4: {e}")

            finally:
                self.rw.save_pushButton.setEnabled(True)
                self.vtk_render_window.SetOffScreenRendering(0)