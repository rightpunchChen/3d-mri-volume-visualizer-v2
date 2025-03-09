# 3d-mri-volume-visualizer-v3(add segmentation)

Add tumor segmentation function 

**Note:** this is just a test example and does not include model weights
To add your own model for tumor segmentation:

1. Modify the 'predict' function inside 'utils/model/infer.py' and put the weights in 'utils/model/checkpoints'.
2. You may also need to modify the weight selection and modalities parts in 'controllers/seg_controller.py' and 'windows/seg_window.py'

## Requirements
- Python 3.9
- PyTorch
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
  - monai==1.4.0
  - nibabel==5.3.2

Install dependencies via pip:
```bash
pip install -r requirements.txt
```
## Usage
Run the following command to start the application:

```bash
python run.py
```
