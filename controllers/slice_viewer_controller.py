import vtk
import imageio
from vtkmodules.util import numpy_support as vtkutil
from PySide6.QtWidgets import QMainWindow, QFileDialog, QProgressDialog, QApplication

from windows.slice_viewer_window import SliceViewer_Window
from windows.message_box import show_error_message
from utils.vtk_tools import *

class SliceViewerController(QMainWindow):
    def __init__(
            self,
            svw: SliceViewer_Window,
            vtk_renderer: vtk.vtkRenderer,
            vtk_render_window: vtk.vtkRenderWindow,
            colors: dict
            ):
        super().__init__()
        self.svw = svw
        self.vtk_renderer = vtk_renderer
        self.vtk_render_window = vtk_render_window
        self.colors = colors
        self.init()
        self.init_actor()
        
        self.brain_image_vtk = None
        self.label_image = None
        self.label_image_vtk = None
        self.pred_image_vtk = None

    def init(self):
        self.svw.BF_btn.clicked.connect(self.open_brain_file) 
        self.svw.LF_btn.clicked.connect(self.open_label_file)
        self.svw.PF_btn.clicked.connect(self.open_prediction_file)

        self.svw.BF_lineEdit.textDropped.connect(self.update_render_button)
        self.svw.LF_lineEdit.textDropped.connect(self.update_label_button)
        self.svw.PF_lineEdit.textDropped.connect(self.update_pred_button)
        self.svw.LF_lineEdit.returnPressed.connect(self.update_label_button)
        self.svw.BF_lineEdit.returnPressed.connect(self.update_render_button)
        self.svw.PF_lineEdit.returnPressed.connect(self.update_pred_button)

        self.svw.LO_spinBox.valueChanged.connect(self.set_label_opacity)
        self.svw.PO_spinBox.valueChanged.connect(self.set_pred_opacity)
        self.svw.slice_horizontalSlider.valueChanged.connect(self.set_slice_value)
        self.svw.render_pushButton.clicked.connect(self.render_brain)
        self.svw.saveMP4_pushButton.clicked.connect(self.save_mp4)
        self.svw.savePNG_pushButton.clicked.connect(self.save_png)

    def init_actor(self):
        self.brain_reslice = None
        self.brain_actor = None
        self.label_actor = None
        self.tp_actor = None
        self.fp_actor = None
        self.fn_actor = None
        self.interactor = self.vtk_render_window.GetInteractor()
        interactor_style = vtk.vtkInteractorStyleRubberBand2D()
        self.interactor.SetInteractorStyle(interactor_style)
        self.interactor.Initialize()

    def open_brain_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.svw.BF_lineEdit.setText(file_path)
        self.update_render_button()
    
    def open_label_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.svw.LF_lineEdit.setText(file_path)
        self.update_label_button()
        
    def open_prediction_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.svw.PF_lineEdit.setText(file_path)
        self.update_pred_button()

    def update_render_button(self):
        self.brain_image_vtk = None
        file_path = self.svw.BF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            self.brain_image_vtk = load_image(file_path)
            self.svw.LF_btn.setEnabled(True)
            self.svw.LF_lineEdit.setEnabled(True)
            self.svw.slice_comboBox.setEnabled(True)
            self.svw.render_pushButton.setEnabled(True)
            return
        elif file_path and not file_exists:
            show_error_message(f"File does not exist: {file_path}")

        self.svw.LF_btn.setEnabled(False)
        self.svw.LF_lineEdit.setEnabled(False)
        self.svw.render_pushButton.setEnabled(False)
        self.svw.slice_comboBox.setEnabled(False)
        self.svw.slice_horizontalSlider.setEnabled(False)
        self.svw.slice_idx_label.setText("")
        self.svw.saveMP4_pushButton.setEnabled(False)
        self.svw.savePNG_pushButton.setEnabled(False)

    def update_label_button(self):
        self.label_image_vtk = None
        self.label_image = None

        file_path = self.svw.LF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            self.label_image_vtk = load_image(file_path)
            self.label_image = vtk_img_to_numpy(self.label_image_vtk)
            max_label_value = self.label_image.max()
            for i in range(1, 6):
                button = getattr(self.svw, f'radioButton_{i}')
                button.setStyleSheet("")
                button.setEnabled(False)
            for i in range(1, min(int(max_label_value) + 1, 6)):
                r = int(self.colors["MASK_COLORS"][i][0]*255)
                g = int(self.colors["MASK_COLORS"][i][1]*255)
                b = int(self.colors["MASK_COLORS"][i][2]*255)
                button = getattr(self.svw, f'radioButton_{i}')
                button.setStyleSheet(f"color: rgb({r}, {g}, {b});")
                button.setEnabled(True)
            self.svw.PF_btn.setEnabled(True)
            self.svw.PF_lineEdit.setEnabled(True)
            return
        elif file_path and not file_exists:
            show_error_message(f"File does not exist: {file_path}")

        for i in range(1, 6):
            button = getattr(self.svw, f'radioButton_{i}')
            button.setStyleSheet("")
            button.setEnabled(False)
        
        self.svw.LO_spinBox.setEnabled(False)
        self.svw.PF_btn.setEnabled(False)
        self.svw.PF_lineEdit.setEnabled(False)
     
    def update_pred_button(self):
        self.pred_image_vtk = None

        file_path = self.svw.PF_lineEdit.text()
        file_exists = check_files(file_path)
        if file_exists:
            self.pred_image_vtk = load_image(file_path)
            for p in ['tp', 'fp', 'fn']:
                r = int(self.colors["PRED_COLORS"][p][0]*255)
                g = int(self.colors["PRED_COLORS"][p][1]*255)
                b = int(self.colors["PRED_COLORS"][p][2]*255)
                button = getattr(self.svw, f'radioButton_{p}')
                button.setStyleSheet(f"color: rgb({r}, {g}, {b});")
                button.setEnabled(True)
            return
        elif file_path and not file_exists:
            show_error_message(f"File does not exist: {file_path}")

        for p in ['tp', 'fp', 'fn']:
            button = getattr(self.svw, f'radioButton_{p}')
            button.setStyleSheet("")
            button.setEnabled(False)
    
    def updata_LO_spinBox(self):
        for i in range(1, 6):
            radio_button = getattr(self.svw, f'radioButton_{i}')
            if radio_button.isChecked() and check_files(self.svw.LF_lineEdit.text()):
                self.svw.LO_spinBox.setEnabled(True)
                return
        self.svw.LO_spinBox.setEnabled(False)
        return
        
    def updata_PO_spinBox(self):
        for i in ['tp', 'fp', 'fn']:
            radio_button = getattr(self.svw, f'radioButton_{i}')
            if radio_button.isChecked() and check_files(self.svw.PF_lineEdit.text()):
                self.svw.PO_spinBox.setEnabled(True)
                return
        self.svw.PO_spinBox.setEnabled(False)
        return
    
    def render_brain(self):
        self.init_actor()
        self.vtk_renderer.RemoveAllViewProps()
        self.svw.saveMP4_pushButton.setEnabled(True)
        self.svw.savePNG_pushButton.setEnabled(True)

        self.orientation = self.svw.slice_comboBox.currentIndex()
        self.dims = self.brain_image_vtk.GetDimensions()

        self.brain_reslice, self.brain_actor = setup_actor_sv(
            self.brain_image_vtk, self.orientation
            )

        label_opacity = self.svw.LO_spinBox.value() / 100
        pred_opacity = self.svw.PO_spinBox.value() / 100
        if self.label_image is not None:
            self.updata_LO_spinBox()
            self.selected_labels = []
            for i in range(1, 6):
                radio_button = getattr(self.svw, f'radioButton_{i}')
                if radio_button.isChecked():
                    self.selected_labels.append(i)
            if self.selected_labels:
                self.label_reslice, self.label_actor = setup_label_actor_sv(
                    self.label_image_vtk,
                    self.orientation,
                    self.selected_labels,
                    self.colors["MASK_COLORS"],
                    label_opacity,
                    )
                self.vtk_renderer.AddActor(self.label_actor)

        if self.pred_image_vtk is not None:
            self.updata_PO_spinBox()
            if self.svw.radioButton_tp.isChecked():
                tp = AND(self.label_image_vtk, self.pred_image_vtk)
                if tp is not None:
                    self.tp_reslice, self.tp_actor = setup_label_actor_sv(
                        tp,
                        self.orientation,
                        None,
                        self.colors["PRED_COLORS"]['tp'],
                        pred_opacity,
                    )
            if self.svw.radioButton_fp.isChecked():
                fp = false_positive(self.label_image_vtk, self.pred_image_vtk)
                if fp is not None:
                    self.fp_reslice, self.fp_actor = setup_label_actor_sv(
                        fp,
                        self.orientation,
                        None,
                        self.colors["PRED_COLORS"]['fp'],
                        pred_opacity,
                    )
            if self.svw.radioButton_fn.isChecked():
                fn = false_negative(self.label_image_vtk, self.pred_image_vtk)
                if fn is not None:
                    self.fn_reslice, self.fn_actor = setup_label_actor_sv(
                        fn,
                        self.orientation,
                        None,
                        self.colors["PRED_COLORS"]['fn'],
                        pred_opacity,
                    )

        self.init_slice_slider()
        self.vtk_renderer.AddActor(self.brain_actor)
        if self.label_actor:
            self.vtk_renderer.AddActor(self.label_actor)
        if self.tp_actor:
            self.vtk_renderer.AddActor(self.tp_actor)
        if self.fp_actor:
            self.vtk_renderer.AddActor(self.fp_actor)
        if self.fn_actor:
            self.vtk_renderer.AddActor(self.fn_actor)

        set_camera_sv(self.vtk_renderer)
        self.vtk_render_window.Render()

    def init_slice_slider(self):
        self.svw.slice_horizontalSlider.setEnabled(True)
        self.svw.slice_horizontalSlider.setMinimum(1)
        if self.orientation == 0:
            max_slice = self.dims[2]
        elif self.orientation == 1:
            max_slice = self.dims[0]
        elif self.orientation == 2:
            max_slice = self.dims[1]
        self.svw.slice_horizontalSlider.setMaximum(max_slice)
        self.svw.slice_horizontalSlider.setValue(max_slice // 2)
        self.svw.slice_idx_label.setText(f"{max_slice // 2}")

    def set_slice_value(self):
        slice_index = self.svw.slice_horizontalSlider.value()
        self.svw.slice_idx_label.setText(f"{slice_index}")
        if self.orientation == 0:
            self.brain_reslice.SetResliceAxesOrigin(0, 0, slice_index-1)
            if self.label_actor:
                self.label_reslice.SetResliceAxesOrigin(0, 0, slice_index-1)
            if self.tp_actor:
                self.tp_reslice.SetResliceAxesOrigin(0, 0, slice_index-1)
            if self.fp_actor:
                self.fp_reslice.SetResliceAxesOrigin(0, 0, slice_index-1)
            if self.fn_actor:
                self.fn_reslice.SetResliceAxesOrigin(0, 0, slice_index-1)
        elif self.orientation == 1:
            self.brain_reslice.SetResliceAxesOrigin(slice_index-1, 0, 0)
            if self.label_actor:
                self.label_reslice.SetResliceAxesOrigin(slice_index-1, 0, 0)
            if self.tp_actor:
                self.tp_reslice.SetResliceAxesOrigin(slice_index-1, 0, 0)
            if self.fp_actor:
                self.fp_reslice.SetResliceAxesOrigin(slice_index-1, 0, 0)
            if self.fn_actor:
                self.fn_reslice.SetResliceAxesOrigin(slice_index-1, 0, 0)
        elif self.orientation == 2:
            self.brain_reslice.SetResliceAxesOrigin(0, slice_index-1, 0)
            if self.label_actor:
                self.label_reslice.SetResliceAxesOrigin(0, slice_index-1, 0)
            if self.tp_actor:
                self.tp_reslice.SetResliceAxesOrigin(0, slice_index-1, 0)
            if self.fp_actor:
                self.fp_reslice.SetResliceAxesOrigin(0, slice_index-1, 0)
            if self.fn_actor:
                self.fn_reslice.SetResliceAxesOrigin(0, slice_index-1, 0)

        self.brain_reslice.Update()
        self.vtk_render_window.Render()

    def set_label_opacity(self):
        opacity = self.svw.LO_spinBox.value() / 100
        if self.label_actor:
            lut = create_label_lut(self.colors["MASK_COLORS"], opacity, self.selected_labels)
            color_mapper = vtk.vtkImageMapToColors()
            color_mapper.SetLookupTable(lut)
            color_mapper.SetInputConnection(self.label_reslice.GetOutputPort())
            color_mapper.SetOutputFormatToRGBA()
            
            self.label_actor.GetMapper().SetInputConnection(color_mapper.GetOutputPort())
            self.vtk_render_window.Render()

    def set_pred_opacity(self):
        opacity = self.svw.PO_spinBox.value() / 100
        if self.tp_actor:
            lut_tp = create_label_lut(self.colors["PRED_COLORS"]["tp"], opacity, None)
            color_mapper_tp = vtk.vtkImageMapToColors()
            color_mapper_tp.SetLookupTable(lut_tp)
            color_mapper_tp.SetInputConnection(self.tp_reslice.GetOutputPort())
            color_mapper_tp.SetOutputFormatToRGBA()
            
            self.tp_actor.GetMapper().SetInputConnection(color_mapper_tp.GetOutputPort())
            self.vtk_render_window.Render()
        if self.fp_actor:
            lut_fp = create_label_lut(self.colors["PRED_COLORS"]["fp"], opacity, None)
            color_mapper_fp = vtk.vtkImageMapToColors()
            color_mapper_fp.SetLookupTable(lut_fp)
            color_mapper_fp.SetInputConnection(self.fp_reslice.GetOutputPort())
            color_mapper_fp.SetOutputFormatToRGBA()
            
            self.fp_actor.GetMapper().SetInputConnection(color_mapper_fp.GetOutputPort())
            self.vtk_render_window.Render()
        if self.fn_actor:
            lut_fn = create_label_lut(self.colors["PRED_COLORS"]["fn"], opacity, None)
            color_mapper_fn = vtk.vtkImageMapToColors()
            color_mapper_fn.SetLookupTable(lut_fn)
            color_mapper_fn.SetInputConnection(self.fn_reslice.GetOutputPort())
            color_mapper_fn.SetOutputFormatToRGBA()
            
            self.fn_actor.GetMapper().SetInputConnection(color_mapper_fn.GetOutputPort())
            self.vtk_render_window.Render()

    def save_mp4(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save MP4 file", "", "MP4 Files (*.mp4)")
        if file_path:
            if not file_path.endswith(('.mp4')):
                file_path = file_path + '.mp4'
            try:
                self.svw.saveMP4_pushButton.setEnabled(False)
                min_slice = self.svw.slice_horizontalSlider.minimum()
                max_slice = self.svw.slice_horizontalSlider.maximum()

                progress_dialog = QProgressDialog("Saving MP4 ... 0%", "Cancel", 0, max_slice, self)
                progress_dialog.setWindowTitle("Saving Progress")
                progress_dialog.setMinimumDuration(0)
                progress_dialog.show()

                window_to_image_filter = vtk.vtkWindowToImageFilter()
                window_to_image_filter.SetInput(self.vtk_render_window)
                window_to_image_filter.SetInputBufferTypeToRGB()
                window_to_image_filter.ReadFrontBufferOff()
                window_to_image_filter.SetScale(1)

                self.vtk_render_window.SetOffScreenRendering(1)

                set_camera_sv(self.vtk_renderer)

                writer = imageio.get_writer(file_path, fps=30, codec="libx264")
                
                for slice_idx in range(min_slice, max_slice + 1):
                    self.svw.slice_horizontalSlider.setValue(slice_idx)
                    self.set_slice_value()
                    self.vtk_render_window.Render()
                    window_to_image_filter.Modified()
                    window_to_image_filter.Update()
                    image_data = window_to_image_filter.GetOutput()
                    width, height, _ = image_data.GetDimensions()

                    frame = vtkutil.vtk_to_numpy(image_data.GetPointData().GetScalars())
                    frame = frame.reshape(height, width, -1)
                    frame = frame[::-1]
                    writer.append_data(frame)

                    progress_dialog.setValue(slice_idx)
                    progress_dialog.setLabelText(f"Saving MP4... {int((slice_idx + 1) / (max_slice + 1) * 100)}%")
                    QApplication.processEvents()
                    if progress_dialog.wasCanceled():
                        raise Exception("Canceled saving.")

                writer.close()
                progress_dialog.setValue(max_slice)

            except Exception as e:
                if os.path.exists(file_path):  
                    os.remove(file_path)
                progress_dialog.setValue(max_slice)
                show_error_message(f"Error saving MP4: {e}")

            finally:
                self.svw.saveMP4_pushButton.setEnabled(True)
                self.vtk_render_window.SetOffScreenRendering(0)

    def save_png(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PNG file", "", "PNG Files (*.png)")
        if file_path:
            if not file_path.endswith(('.png')):
                file_path = file_path + '.png'
            try:
                window_to_image_filter = vtk.vtkWindowToImageFilter()
                window_to_image_filter.SetInput(self.vtk_render_window)
                window_to_image_filter.SetInputBufferTypeToRGB()
                window_to_image_filter.ReadFrontBufferOff()
                window_to_image_filter.SetScale(1)

                self.vtk_render_window.SetOffScreenRendering(1)

                set_camera_sv(self.vtk_renderer)

                self.vtk_render_window.Render()
                window_to_image_filter.Modified()
                window_to_image_filter.Update()
                image_data = window_to_image_filter.GetOutput()

                writer = vtk.vtkPNGWriter()
                writer.SetFileName(file_path)
                writer.SetInputData(image_data)
                writer.Write()

            except Exception as e:
                if os.path.exists(file_path):  
                    os.remove(file_path)
                show_error_message(f"Error saving PNG: {e}")

            finally:
                self.svw.savePNG_pushButton.setEnabled(True)
                self.vtk_render_window.SetOffScreenRendering(0)