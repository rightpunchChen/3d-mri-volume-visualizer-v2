from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QGridLayout, QSizePolicy, QTabWidget, QMenuBar
)


from windows.render_window import Render_Window
from windows.slice_viewer_window import SliceViewer_Window
from windows.multi_slice_viewer_window import MultiSliceViewer_Window
from windows.mesh_viewer_window import MeshViewer_Window
from utils.configs import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(950, 620)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setMovable(False)

        # self.home_page = QWidget()
        # self.home_page.setObjectName(u"home_page")
        # self.tabWidget.addTab(self.home_page, "Home")


        self.vtk_page = QWidget()
        self.vtk_page.setObjectName(u"vtk_page")
        self.tabWidget.addTab(self.vtk_page, "vtk Page")
        self.vtk_window_layout = QHBoxLayout(self.vtk_page)
        self.vtk_window_layout.setContentsMargins(10, 10, 10, 10)
        self.vtk_window_layout.setSpacing(10)
        self.vtk_window_tabWidget = QTabWidget(self.vtk_page)
        self.vtk_window_tabWidget.setObjectName(u"tabWidget")
        self.vtk_window_tabWidget.setEnabled(True)
        self.vtk_window_tabWidget.setMovable(False)
        self.vtk_window_tabWidget.setFixedWidth(320)
        self.rw = Render_Window(self.vtk_page)
        self.vtk_window_tabWidget.addTab(self.rw.render_panel, "3D Render")
        self.svw = SliceViewer_Window(self.vtk_page)
        self.vtk_window_tabWidget.addTab(self.svw.sv_panel, "Slice Viewer")
        self.vtk_window_layout.addWidget(self.vtk_window_tabWidget)
        self.render = QWidget(self.vtk_page)
        self.render.setObjectName("render")
        self.render.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vtk_window_layout.addWidget(self.render)
        

        self.msvw_page = QWidget()
        self.msvw_page.setObjectName(u"msvw_page")
        self.tabWidget.addTab(self.msvw_page, "Multi Slice Viewer")
        self.msvw = MultiSliceViewer_Window(self.msvw_page)


        self.mv_page = QWidget()
        self.mv_page.setObjectName(u"mv_page")
        self.tabWidget.addTab(self.mv_page, "Mesh Viewer")
        self.mv = MeshViewer_Window(self.mv_page)


        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menuBar)
        self.settings_menu = self.menuBar.addMenu("Settings")
        self.retranslateUi(MainWindow)
        # self.tabWidget.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))