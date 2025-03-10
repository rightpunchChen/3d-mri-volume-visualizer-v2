import os
import sys
import numpy as np
import torch
import torch.nn as nn
import nibabel as nib
from monai.inferers import sliding_window_inference
from monai.networks.nets import DynUNet
from monai.transforms import (
    Compose, ToTensor, NormalizeIntensity, EnsureType, EnsureChannelFirst)
    
class nnUNet(nn.Module):
    def __init__(self):
        super(nnUNet, self).__init__()
        filters = [32, 64, 128, 256, 512, 512]
        strides, kernels = [], []
        kernels = [[3, 3, 3] for _ in range(len(filters))]
        strides = [[2, 2, 2] for _ in range(len(filters) - 1)]
        strides.insert(0, [1, 1, 1])
        self.model = nn.Sequential(
            DynUNet(
                spatial_dims = 3,
                in_channels = 4,
                out_channels = 3,
                kernel_size = kernels,
                strides = strides,
                filters = filters,
                upsample_kernel_size = strides[1:],
                deep_supervision = True,
                deep_supr_num = 3,
                res_block = True,
                norm_name = ("Group", {"num_groups": 8, "affine": True}),
                trans_bias=True
            ),
            nn.Sigmoid()
        )
        
    def load(self, path):
        weight = torch.load(path, map_location=torch.device('cpu'))
        has_model = any(k.startswith('model.') for k in weight.keys())

        if has_model:
            from collections import OrderedDict
            new_state_dict = OrderedDict((k[6:], v) for k, v in weight.items())  # remove 'module.'
            self.model.load_state_dict(new_state_dict)
        else:
            self.model.load_state_dict(weight)
        return

    def forward(self, x):
        return self.model(x)
    
def predict(image, checkpoint, save_prob_dir, image_name):
    if sys.platform == 'darwin':
        device = torch.device('cpu')
    else:
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    model = nnUNet()
    if checkpoint == "MET":
        check_point = "./utils/model/checkpoints/MET.pth"
    model.load(check_point)
    model.to(device)
    model.eval()

    image_stacked = np.stack([i for i in image], axis=-1)

    inference_transforms = Compose([
        EnsureChannelFirst(channel_dim=-1),
        NormalizeIntensity(nonzero=True, channel_wise=True),
        ToTensor(),
        EnsureType(),
    ])
    data = inference_transforms(image_stacked)

    with torch.no_grad():
        data = data.unsqueeze(0).to(device, dtype=torch.float)
        pred = sliding_window_inference(
            inputs=data,
            roi_size=(128, 128, 128),
            sw_batch_size=4,
            predictor=model,
            overlap=0.5
            ).squeeze().cpu().detach().numpy()
        
        wt_pred = (pred[0] >= 0.5).astype('uint8')
        tc_pred = (pred[1] >= 0.5).astype('uint8')
        et_pred = (pred[2] >= 0.5).astype('uint8')
        pred_final = np.zeros_like(wt_pred)
        pred_final[wt_pred == 1] = 2
        pred_final[tc_pred == 1] = 1
        pred_final[et_pred == 1] = 3

    nib.save(
        nib.Nifti1Image(pred_final.T, np.eye(4)),
        os.path.join(save_prob_dir, f"{image_name}-seg.nii.gz")
        )