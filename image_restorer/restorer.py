import os
import torch
from runpy import run_path
from skimage import img_as_ubyte
import cv2
import torch.nn.functional as F
import urllib.request

# task will be defined by the user input from views.py
parameters = {
    'inp_channels':3,
    'out_channels':3, 
    'n_feat':80,
    'chan_factor':1.5,
    'n_RRG':4,
    'n_MRB':2,
    'height':3,
    'width':2,
    'bias':False,
    'scale':1,
    'task': task
}