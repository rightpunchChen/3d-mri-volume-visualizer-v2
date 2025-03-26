import os
import itk
import SimpleITK as sitk
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog
    )
from windows.reg_window import Registration_Window
from utils.vtk_tools import *
from windows.message_box import show_error_message
class RegistrationController(QMainWindow):
    def __init__(
            self,
            regw: Registration_Window,
            ):
        super().__init__()
        self.regw = regw
        self.init()

    def init(self):
        self.regw.fixed_image_btn.clicked.connect(self.open_fix_data)
        self.regw.moving_image_btn.clicked.connect(self.open_move_data)
        self.regw.fixed_image_lineEdit.returnPressed.connect(self.update_run_button)
        self.regw.fixed_image_lineEdit.textDropped.connect(self.update_run_button)
        self.regw.moving_image_lineEdit.returnPressed.connect(self.update_run_button)
        self.regw.moving_image_lineEdit.textDropped.connect(self.update_run_button)
        self.regw.registration_btn.clicked.connect(self.run_registration)

    def open_fix_data(self):
        fix_file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.regw.fixed_image_lineEdit.setText(fix_file_path)
        self.update_run_button()

    def open_move_data(self, idx):
        move_file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.regw.moving_image_lineEdit.setText(move_file_path)
        self.update_run_button()

    def update_run_button(self):
        fix_path = self.regw.fixed_image_lineEdit.text()
        moving_path = self.regw.moving_image_lineEdit.text()
        file_exists = check_files(fix_path) & check_files(moving_path)
        if file_exists:
            self.regw.registration_btn.setEnabled(True)
            return
        elif fix_path and moving_path and not file_exists:
            show_error_message(f"File does not exist: ")

        self.regw.registration_btn.setEnabled(False)

    def run_registration(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "nii.gz Files (*.nii.gz)")
        if save_path:
            if not save_path.endswith(('.nii.gz')) and not save_path.endswith(('.nii')):
                save_path += '.nii.gz'
            try:
                self.regw.registration_btn.setEnabled(False)
                fixed_path = self.regw.fixed_image_lineEdit.text()
                moving_path = self.regw.moving_image_lineEdit.text()

                t2_img = sitk.ReadImage(fixed_path)

                origin = t2_img.GetOrigin()
                direction = t2_img.GetDirection()
                spacing = t2_img.GetSpacing()

                _, param = self.registration(fixed_path, moving_path, None, None)
                param.SetParameter('FinalBSplineInterpolationOrder', '0')
                label_image = itk.imread(moving_path, itk.F)
                transform_label_image = itk.transformix_filter(label_image, param)
                itk.imwrite(transform_label_image, save_path)

                img_reg = sitk.ReadImage(save_path)
                img_reg.SetOrigin(origin)
                img_reg.SetDirection(direction)
                img_reg.SetSpacing(spacing)
                sitk.WriteImage(img_reg, save_path)

            except Exception as e:
                show_error_message(f"Error saving file: {e}")

            finally:
                self.regw.registration_btn.setEnabled(True)





    def registration(self, Fixed_image, Moving_image, Label_image, LabelOutput, Label_2=None, LabelOut_2=None):
        fixed_image = itk.imread(Fixed_image, itk.F)
        moving_image = itk.imread(Moving_image, itk.F)
        parameter_object = itk.ParameterObject.New()
        parameter_map_rigid = parameter_object.GetDefaultParameterMap('rigid')
        parameter_object.AddParameterMap(parameter_map_rigid)
        result_registered_image, result_transform_parameters = itk.elastix_registration_method(
            fixed_image, moving_image, parameter_object=parameter_object)

        if Label_image:
            result_transform_parameters.SetParameter('FinalBSplineInterpolationOrder', '0')
            label_image = itk.imread(Label_image, itk.F)
            transform_label_image = itk.transformix_filter(label_image, result_transform_parameters)
            itk.imwrite(transform_label_image, LabelOutput)
        if Label_2:
            result_transform_parameters.SetParameter('FinalBSplineInterpolationOrder', '0')
            label_image = itk.imread(Label_2, itk.F)
            transform_label_image = itk.transformix_filter(label_image, result_transform_parameters)
            itk.imwrite(transform_label_image, LabelOut_2)
        return result_registered_image, result_transform_parameters