# 3d-mri-volume-visualizer-v2

This application provides a GUI for visualizing brain, label and prediction images for observing the model predictions using VTK and PySide6. Users can load NIFTI files, visualize them in 3D, and save a rotating view as an MP4 file.

The updated version includes a slice viewer for cross-sectional analysis and a mesh viewer for 3D surface visualization.

<img src="https://github.com/rightpunchChen/3d-mri-volume-visualizer-v2/blob/main/demo.png" width="65%"> <img src="https://github.com/rightpunchChen/3d-mri-volume-visualizer-v2/blob/main/demo_msvw.png" width="65%">

**Note:** This version does not include the segmentation function. For the segmentation version, please refer to the [seg branch](https://github.com/rightpunchChen/3d-mri-volume-visualizer-v2/tree/seg).

## Requirements
- Python 3.9
- Required Python Libraries:
  - imageio==2.37.0
  - imageio-ffmpeg==0.6.0
  - matplotlib==3.9.4
  - numpy==2.0.2
  - PySide6==6.8.1.1
  - vtk==9.4.1
  - scipy==1.13.1
  - plotly==6.0.0
  - SimpleITK==2.4.1

Install dependencies via pip:
```bash
pip install -r requirements.txt
```
## Usage
Run the following command to start the application:

```bash
python run.py
```
