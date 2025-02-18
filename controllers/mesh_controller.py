import scipy.io as sio
import plotly.graph_objects as go
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog
    )
from windows.mesh_viewer_window import MeshViewer_Window
from windows.message_box import show_error_message
from utils.vtk_tools import *

class MeshViewerController(QMainWindow):
    def __init__(
            self,
            mvw: MeshViewer_Window,
            ):
        super().__init__()
        self.mvw = mvw
        self.init()

    def init(self):
        self.mvw.mesh_data_btn.clicked.connect(self.open_mesh_file)
        self.mvw.mesh_data_lineEdit.returnPressed.connect(self.open_mesh_file)
        self.mvw.mesh_data_lineEdit.textDropped.connect(self.open_mesh_file)
        self.mvw.render_btn.clicked.connect(self.run_meshviewer)

    def open_mesh_file(self):
        data_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Mesh file",
            "",
            "Mesh Files (*.mat *.npz)"
            )
        self.mvw.mesh_data_lineEdit.setText(data_file_path)
        file_exists = check_files(data_file_path)
        if file_exists:
            self.mvw.render_btn.setEnabled(True)
            return
        elif data_file_path and not file_exists:
            show_error_message(f"File does not exist: {data_file_path}")

        self.mvw.render_btn.setEnabled(False)

    def run_meshviewer(self):
        path = self.mvw.mesh_data_lineEdit.text()
        if path.lower().endswith("mat"):
            mesh = sio.loadmat(path)
            T = mesh["T"] - 1
            V = mesh["V"]
        elif path.lower().endswith("npz"):
            mesh = np.load(path)
            T = mesh["T"]
            V = mesh["V"]
        self.Plot(T, V)

    def BoundaryFace(self, T):
        '''Subfunction of Tet.Plot'''
        F         = np.r_[T[:,[0,1,2]], T[:,[0,3,1]], T[:,[1,3,2]],T[:,[2,3,0]]]
        _, ii, jj = np.unique( np.sort(F, axis=1), axis=0, return_index=True, return_inverse=True)
        F         = F[ii,:]
        ss = np.bincount(jj, minlength=F.shape[0])
        Fb = F[ss==1,:]
        return Fb

    def Plot(self, T, V, ratio=0.2, axis=0):
        ip     = np.unique(T)
        dd     = np.max(V[ip,0]) - np.min(V[ip,0])
        ok     = np.zeros(V.shape[0], dtype=bool)
        ok[ip] = V[ip,axis] < np.mean(V[ip,axis]) + (ratio*dd)
        ti     = np.all(ok[T], axis=1)

        F1        = self.BoundaryFace(T[ ti,:])
        F2        = self.BoundaryFace(T[~ti,:])
        F1_sorted = np.sort(F1, axis=1)
        F2_sorted = np.sort(F2, axis=1)
        c1 = np.sum(np.isin(F1_sorted, F2_sorted), axis=1) == 3
        c2 = np.sum(np.isin(F2_sorted, F1_sorted), axis=1) == 3

        # define external surface
        meshes_E = go.Mesh3d(
            x=V[:,0],
            y=V[:,1],
            z=V[:,2],
            color='rgb(138,241,255)',
            i=F1[~c1,0],
            j=F1[~c1,1],
            k=F1[~c1,2],
            name='external surface',
            lighting=dict(ambient=1),
            showscale=True
        )
        tri_points1 = V[F1[~c1,:]]
        Xe1 = []; Ye1 = []; Ze1 = []
        for Fpoint in tri_points1:
            Xe1.extend( [Fpoint[k%3][0] for k in range(4)]+[None] )
            Ye1.extend( [Fpoint[k%3][1] for k in range(4)]+[None] )
            Ze1.extend( [Fpoint[k%3][2] for k in range(4)]+[None] )
        lines_E = go.Scatter3d(
            x=Xe1,
            y=Ye1,
            z=Ze1,
            mode='lines',
            name='external line',
            line=dict(color='rgb(51,51,51)',
                    width=2)
        )

        # define internal surface
        meshes_I = go.Mesh3d(
            x=V[:,0],
            y=V[:,1],
            z=V[:,2],
            color='rgb(242.25,242.25,127.5)',
            i=F1[c1,0],
            j=F1[c1,1],
            k=F1[c1,2],
            name='internal surface',
            lighting=dict(ambient=1),
            showscale=True
        )
        tri_points2 = V[F1[c1,:]]
        Xe2 = []; Ye2 = []; Ze2 = []
        for Fpoint in tri_points2:
            Xe2.extend( [Fpoint[k%3][0] for k in range(4)]+[None] )
            Ye2.extend( [Fpoint[k%3][1] for k in range(4)]+[None] )
            Ze2.extend( [Fpoint[k%3][2] for k in range(4)]+[None] )
        lines_I = go.Scatter3d(
            x=Xe2,
            y=Ye2,
            z=Ze2,
            mode='lines',
            name='internal line',
            line=dict(color='rgb(63.75,63.75,63.75)',
                    width=2)
        )

        # transparent part
        meshes_T = go.Mesh3d(
            x=V[:,0],
            y=V[:,1],
            z=V[:,2],
            color='rgb(138,241,255)',
            i=F2[~c2,0],
            j=F2[~c2,1],
            k=F2[~c2,2],
            name='transparent surface',
            lighting=dict(ambient=1),
            showscale=True,
            opacity=0.2
        )

        fig = go.Figure(data=[meshes_E, lines_E,
                            meshes_I, lines_I,
                            meshes_T])
        fig.show()
        return 