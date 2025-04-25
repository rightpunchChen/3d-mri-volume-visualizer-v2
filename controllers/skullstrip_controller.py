import SimpleITK as sitk
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog
    )
from windows.skull_strip_window import SkullStrip_Window
from utils.vtk_tools import *
from windows.message_box import *
import subprocess
import torch


class SkullStripController(QMainWindow):
    def __init__(
            self,
            strip: SkullStrip_Window,
            ):
        super().__init__()
        self.strip = strip
        self.init()

    def init(self):
        self.strip.input_image_btn.clicked.connect(self.open_input_image)
        self.strip.skullstrip_btn.clicked.connect(self.run_skullstrip)
        self.strip.input_image_lineEdit.returnPressed.connect(self.update_run_button)
        self.strip.input_image_lineEdit.textDropped.connect(self.update_run_button)

    def open_input_image(self):
        input_file_path, _ = QFileDialog.getOpenFileName(self,"Select NII files", "", "NII Files (*.nii *.nii.gz)")
        self.strip.input_image_lineEdit.setText(input_file_path)
        self.update_run_button()

    def update_run_button(self):
        input_path = self.strip.input_image_lineEdit.text()
        file_exists = check_files(input_path)
        if file_exists:
            self.strip.skullstrip_btn.setEnabled(True)
            return
        elif input_path and not file_exists:
            show_error_message(f"File does not exist: ")

        self.strip.skullstrip_btn.setEnabled(False)

    def run_skullstrip(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "nii.gz Files (*.nii.gz)")
        if save_path:
            if not save_path.endswith(('.nii.gz')) and not save_path.endswith(('.nii')):
                save_path += '.nii.gz'
            try:
                self.strip.skullstrip_btn.setEnabled(False)
                input_path = self.strip.input_image_lineEdit.text()
                output_path = save_path
                from HD_BET.paths import folder_with_parameter_files
                os.makedirs(folder_with_parameter_files, exist_ok=True)
                if torch.cuda.is_available():
                    cmd = f"hd-bet -i {input_path} -o {output_path} -device 0"
                    subprocess.run(cmd, shell=True)
                else:
                    cmd = f"hd-bet -i {input_path} -o {output_path} -device cpu -tta 0"
                    subprocess.run(cmd, shell=True)
                show_info_message("Skull stripping completed")

            except Exception as e:
                show_error_message(f"Error: {e}")
            finally:
                self.strip.skullstrip_btn.setEnabled(True)