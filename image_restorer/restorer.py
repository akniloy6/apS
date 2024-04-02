import os
import torch
import cv2
from runpy import run_path
import torch.nn.functional as F
from skimage import img_as_ubyte
from flask import (
    Flask,
    send_from_directory,
    jsonify,
    request,
    flash,
    redirect,
    render_template,
)
Device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
task = "lowlight_enhancement"
parameters = {
    "inp_channels": 3,
    "out_channels": 3,
    "n_feat": 80,
    "chan_factor": 1.5,
    "n_RRG": 4,
    "n_MRB": 2,
    "height": 3,
    "width": 2,
    "bias": False,
    "scale": 1,
    "task": task,
}

config = {
    "weights_1": os.path.join(
        "Enhancement", "pretrained_models", "enhancement_lol.pth"
    ),
    "architecture": run_path(
        os.path.join("basicsr", "models", "archs", "mirnet_v2_arch.py")
    ),
    "model_name": "MIRNet_v2",
    "task": "lowlight_enhancement",
    "input_dir": "demo/sample_images/" + task + "/degraded",
    "output_dir": "static/images/restored",
    "img_multiple_of": 4,
}

input_dir = config["input_dir"]
out_dir = config["output_dir"]
os.makedirs(out_dir, exist_ok=True)
weights = config["weights_1"]
load_arch = config["architecture"]
model = load_arch["MIRNet_v2"](**parameters)
model.cuda()

checkpoint = torch.load(weights)
model.load_state_dict(checkpoint["params"])
model.eval()
img_multiple_of = config["img_multiple_of"]


def prediction(filepath):
    """
    This function takes a filepath to an image and returns a tensor representation of the image after performing
    certain operations. It uses a pre-trained model to make predictions on the image.

    The function first clears the CUDA cache, then reads the image file, converts it to RGB, and transforms it into
    a tensor. The tensor is then normalized by dividing all its values by 255.

    Parameters:
    filepath (str): The path to the image file.

    Returns:
    torch.Tensor: The tensor representation of the image.

    """
    with torch.no_grad():
        # print(file_)

        torch.cuda.ipc_collect()
        torch.cuda.empty_cache()
        img = cv2.cvtColor(cv2.imread(filepath), cv2.COLOR_BGR2RGB)
        input_ = (
            torch.from_numpy(img)
            .float()
            .div(255.0)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .cuda()
        )

        # Pad the input if not_multiple_of 4
        h, w = input_.shape[2], input_.shape[3]
        H, W = ((h + img_multiple_of) // img_multiple_of) * img_multiple_of, (
            (w + img_multiple_of) // img_multiple_of
        ) * img_multiple_of
        padh = H - h if h % img_multiple_of != 0 else 0
        padw = W - w if w % img_multiple_of != 0 else 0
        input_ = F.pad(input_, (0, padw, 0, padh), "reflect")

        restored = model(input_)
        restored = torch.clamp(restored, 0, 1)

        # Unpad the output
        restored = restored[:, :, :h, :w]
        restored = restored.permute(0, 2, 3, 1).cpu().detach().numpy()
        restored = img_as_ubyte(restored[0])
        restored_image = cv2.cvtColor(restored, cv2.COLOR_RGB2BGR)
        return restored_image
