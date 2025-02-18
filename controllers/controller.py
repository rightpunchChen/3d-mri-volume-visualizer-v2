import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PySide6.QtWidgets import QMainWindow, QVBoxLayout

from controllers.render_controller import RenderController
from controllers.slice_viewer_controller import SliceViewerController
from controllers.multi_slice_viewer_controller import MultiSliceViewerController
from controllers.mesh_controller import MeshViewerController
from windows.colors_settings_dialog import ColorsSettingsDialog
from windows.ui_window_v2 import Ui_MainWindow
from utils.vtk_tools import *
from utils.configs import *

class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.rw = self.ui.rw
        self.svw = self.ui.svw
        self.msvw = self.ui.msvw
        self.mv = self.ui.mv
        self.colors = DEFAULT_COLORS

        self.settings_action = self.ui.settings_menu.addAction("Color Settings")
        self.settings_action.triggered.connect(self.open_color_settings)

        self.render_layout = QVBoxLayout(self.ui.render)
        self.render_layout.setContentsMargins(0, 0, 0, 0)
        self.vtk_widget = QVTKRenderWindowInteractor(self.ui.render)
        self.render_layout.addWidget(self.vtk_widget)  # Add the VTK widget to the layout

        self.vtk_renderer = vtk.vtkRenderer()
        self.vtk_renderer.SetBackground(self.colors["BACKGROUND_COLORS"])
        self.vtk_render_window = self.vtk_widget.GetRenderWindow()
        self.vtk_render_window.AddRenderer(self.vtk_renderer)
        self.interactor = self.vtk_render_window.GetInteractor()
        self.interactor.Initialize()

        self.rwController = RenderController(
            self.rw,
            self.vtk_renderer,
            self.vtk_render_window,
            self.colors
            )
        self.svwController = SliceViewerController(
            self.svw,
            self.vtk_renderer,
            self.vtk_render_window,
            self.colors
            )

        self.msvwController = MultiSliceViewerController(
            self.msvw, self.colors
        )

        self.mvController = MeshViewerController(
            self.mv
        )
        
    def open_color_settings(self):
        dialog = ColorsSettingsDialog(self.colors, DEFAULT_COLORS)
        dialog.color_updated.connect(self.update_colors)
        dialog.exec()

    def update_colors(self, new_colors):
        self.colors = new_colors
        self.vtk_renderer.SetBackground(self.colors["BACKGROUND_COLORS"])

        self.rwController.colors = self.colors
        self.rwController.update_label_button()
        self.rwController.update_pred_button()

        self.svwController.colors = self.colors
        self.svwController.update_label_button()
        self.svwController.update_pred_button()

        self.msvwController.colors = self.colors
        self.vtk_render_window.Render()