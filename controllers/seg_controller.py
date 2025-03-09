import vtk
import imageio
import SimpleITK as sitk
from vtkmodules.util import numpy_support as vtkutil
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QProgressDialog, QApplication, QMessageBox
    )

from windows.seg_window import Segmentation_Window
from windows.message_box import show_error_message
from utils.vtk_tools import *
from utils.model.infer import predict

class SegmentationController(QMainWindow):
    def __init__(
            self,
            segw: Segmentation_Window,
            vtk_renderer: vtk.vtkRenderer,
            vtk_render_window: vtk.vtkRenderWindow,
            colors: dict
            ):
        super().__init__()
        self.segw = segw
        self.modalities = ["t2f", "t1n", "t1c", "t2w"]
        self.vtk_renderer = vtk_renderer
        self.vtk_render_window = vtk_render_window
        self.colors = colors

        self.brain_image_vtk = None
        self.label_image_vtk = None

        self.init()
        self.init_actor()
        self.init_file_name()

    def init(self):
        self.segw.BF_btn.clicked.connect(self.open_brain_folder) 
        self.segw.BF_lineEdit.textDropped.connect(self.update_run_button)
        self.segw.BF_lineEdit.returnPressed.connect(self.update_run_button)
        self.segw.LO_spinBox.valueChanged.connect(self.set_label_opacity)
        self.segw.slice_horizontalSlider.valueChanged.connect(self.set_slice_value)
        self.segw.seg_pushButton.clicked.connect(self.run_seg)
        self.segw.render_pushButton.clicked.connect(self.render_brain)
        self.segw.saveMP4_pushButton.clicked.connect(self.save_mp4)
        self.segw.savePNG_pushButton.clicked.connect(self.save_png)

    def init_actor(self):
        self.brain_actor = None
        self.label_actor = None
        self.interactor = self.vtk_render_window.GetInteractor()
        interactor_style = vtk.vtkInteractorStyleRubberBand2D()
        self.interactor.SetInteractorStyle(interactor_style)
        self.interactor.Initialize()

    def init_file_name(self):
        for m in self.modalities:
            setattr(self, f'{m}_file', None)
        self.label_file = None
        self.brain_image_vtk = None
        self.label_image_vtk = None

    def open_brain_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Brain Folder")
        self.segw.BF_lineEdit.setText(folder_path)
        self.update_run_button()

    def update_run_button(self):
        folder_path = self.segw.BF_lineEdit.text()
        file_exists = check_files(folder_path)
        if file_exists:
            flag = 1
            folder_name = os.path.basename(os.path.normpath(folder_path))

            for m in self.modalities:
                path = os.path.join(folder_path, folder_name+f'-{m}.nii.gz')
                if check_files(path):
                    img = sitk.GetArrayFromImage(sitk.ReadImage(path))
                    setattr(self, f'{m}_file', img)
                else:
                    flag = 0
                    show_error_message(f"File does not exist: {path}")
                    break
            if flag:
                self.segw.seg_pushButton.setEnabled(True)
                self.segw.model_comboBox.setEnabled(True)
                return

        elif folder_path and not file_exists:
            show_error_message(f"File does not exist: {folder_path}")

        for i in range(1, 6):
            button = getattr(self.segw, f'radioButton_{i}')
            button.setStyleSheet("")
            button.setEnabled(False)
        self.segw.render_pushButton.setEnabled(False)
        self.segw.LO_spinBox.setEnabled(False)
        self.segw.slice_horizontalSlider.setEnabled(True)
        self.segw.slice_comboBox.setEnabled(True)
        self.segw.saveMP4_pushButton.setEnabled(False)
        self.segw.savePNG_pushButton.setEnabled(False)
        self.segw.seg_pushButton.setEnabled(False)
        self.segw.model_comboBox.setEnabled(False)
        self.segw.BF_lineEdit.setText("")
        self.init_file_name()

    def render_brain(self):
        self.init_actor()
        self.vtk_renderer.RemoveAllViewProps()
        self.segw.saveMP4_pushButton.setEnabled(True)
        self.segw.savePNG_pushButton.setEnabled(True)

        self.orientation = self.segw.slice_comboBox.currentIndex()
        self.dims = self.brain_image_vtk.GetDimensions()

        self.brain_reslice, self.brain_actor = setup_actor_sv(
            self.brain_image_vtk, self.orientation
            )

        label_opacity = self.segw.LO_spinBox.value() / 100

        self.updata_LO_spinBox()
        self.selected_labels = []
        for i in range(1, 6):
            radio_button = getattr(self.segw, f'radioButton_{i}')
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

        self.init_slice_slider()
        self.vtk_renderer.AddActor(self.brain_actor)
        self.vtk_renderer.AddActor(self.label_actor)

        set_camera_sv(self.vtk_renderer)
        self.vtk_render_window.Render()

    def updata_LO_spinBox(self):
        for i in range(1, 6):
            radio_button = getattr(self.segw, f'radioButton_{i}')
            if radio_button.isChecked():
                self.segw.LO_spinBox.setEnabled(True)
                return
        self.segw.LO_spinBox.setEnabled(False)
        return
    
    def init_slice_slider(self):
        self.segw.slice_horizontalSlider.setEnabled(True)
        self.segw.slice_horizontalSlider.setMinimum(1)
        if self.orientation == 0:
            max_slice = self.dims[2]
        elif self.orientation == 1:
            max_slice = self.dims[0]
        elif self.orientation == 2:
            max_slice = self.dims[1]
        self.segw.slice_horizontalSlider.setMaximum(max_slice)
        self.segw.slice_horizontalSlider.setValue(max_slice // 2)
        self.segw.slice_idx_label.setText(f"{max_slice // 2}")

    def set_slice_value(self):
        slice_index = self.segw.slice_horizontalSlider.value()
        self.segw.slice_idx_label.setText(f"{slice_index}")
        if self.orientation == 0:
            self.brain_reslice.SetResliceAxesOrigin(0, 0, slice_index-1)
            if self.label_actor:
                self.label_reslice.SetResliceAxesOrigin(0, 0, slice_index-1)
        elif self.orientation == 1:
            self.brain_reslice.SetResliceAxesOrigin(slice_index-1, 0, 0)
            if self.label_actor:
                self.label_reslice.SetResliceAxesOrigin(slice_index-1, 0, 0)
        elif self.orientation == 2:
            self.brain_reslice.SetResliceAxesOrigin(0, slice_index-1, 0)
            if self.label_actor:
                self.label_reslice.SetResliceAxesOrigin(0, slice_index-1, 0)

        self.brain_reslice.Update()
        self.vtk_render_window.Render()

    def set_label_opacity(self):
        opacity = self.segw.LO_spinBox.value() / 100
        if self.label_actor:
            lut = create_label_lut(self.colors["MASK_COLORS"], opacity, self.selected_labels)
            color_mapper = vtk.vtkImageMapToColors()
            color_mapper.SetLookupTable(lut)
            color_mapper.SetInputConnection(self.label_reslice.GetOutputPort())
            color_mapper.SetOutputFormatToRGBA()
            
            self.label_actor.GetMapper().SetInputConnection(color_mapper.GetOutputPort())
            self.vtk_render_window.Render()

    def run_seg(self):
        self.segw.BF_btn.setEnabled(False)
        self.segw.BF_lineEdit.setEnabled(False)

        folder_path = self.segw.BF_lineEdit.text()
        folder_name = os.path.basename(os.path.normpath(folder_path))
        label_path = os.path.join(folder_path, folder_name+f'-seg.nii.gz')

        if check_files(label_path):
            reply = QMessageBox.question(
                self, 
                "Confirm", 
                "Seg file exists. Continue segmentation?", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                self.segw.BF_btn.setEnabled(True)
                self.segw.BF_lineEdit.setEnabled(True)
                return
            
        try:
            predict(
                [getattr(self, f'{m}_file') for m in self.modalities],
                self.segw.model_comboBox.currentText(),
                folder_path,
                folder_name
                )
        except Exception as e:
            show_error_message(f"Error predicting: {e}")
            return

        folder_path = self.segw.BF_lineEdit.text()
        folder_name = os.path.basename(os.path.normpath(folder_path))
        label_path = os.path.join(folder_path, folder_name+f'-seg.nii.gz')

        self.label_file = sitk.GetArrayFromImage(sitk.ReadImage(label_path))

        self.brain_image_vtk = load_image(os.path.join(folder_path, folder_name+f'-t2f.nii.gz'))
        self.label_image_vtk = load_image(label_path)

        max_label_value = self.label_file.max()
        for i in range(1, min(int(max_label_value) + 1, 6)):
            r = int(self.colors["MASK_COLORS"][i][0]*255)
            g = int(self.colors["MASK_COLORS"][i][1]*255)
            b = int(self.colors["MASK_COLORS"][i][2]*255)
            button = getattr(self.segw, f'radioButton_{i}')
            button.setStyleSheet(f"color: rgb({r}, {g}, {b});")
            button.setEnabled(True)

        self.segw.BF_btn.setEnabled(True)
        self.segw.BF_lineEdit.setEnabled(True)
        self.segw.render_pushButton.setEnabled(True)
        self.segw.slice_comboBox.setEnabled(True)

    def save_mp4(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save MP4 file", "", "MP4 Files (*.mp4)")
        if file_path:
            if not file_path.endswith(('.mp4')):
                file_path = file_path + '.mp4'
            try:
                self.segw.saveMP4_pushButton.setEnabled(False)
                min_slice = self.segw.slice_horizontalSlider.minimum()
                max_slice = self.segw.slice_horizontalSlider.maximum()

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
                    self.segw.slice_horizontalSlider.setValue(slice_idx)
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
                self.segw.saveMP4_pushButton.setEnabled(True)
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
                self.segw.savePNG_pushButton.setEnabled(True)
                self.vtk_render_window.SetOffScreenRendering(0)