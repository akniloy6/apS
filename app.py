import os
import torch
from flask import Flask, send_from_directory, jsonify
from runpy import run_path
from skimage import img_as_ubyte
import cv2
import torch.nn.functional as F

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])







task = 'lowlight_enhancement'
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

config = {  
    'weights': os.path.join('Enhancement', 'pretrained_models', 'enhancement_lol.pth'),
    'architecture': run_path(os.path.join('basicsr', 'models', 'archs', 'mirnet_v2_arch.py')),
    'model_name': 'MIRNet_v2',
    'task': 'lowlight_enhancement',
    'input_dir': 'demo/sample_images/'+task+'/degraded',
    'output_dir': 'demo/sample_images/'+task+'/restored',
    'img_multiple_of': 4

}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

input_dir = config['input_dir']
out_dir = config['output_dir']
os.makedirs(out_dir, exist_ok=True)
weights = config['weights']
load_arch = config['architecture']
model = load_arch['MIRNet_v2'](**parameters)
model.cuda()
checkpoint = torch.load(weights)
model.load_state_dict(checkpoint['params'])
model.eval()



img_multiple_of = config['img_multiple_of']
@app.route('/predict/<filename>')   
def prediction(filepath):
    with torch.no_grad():

        # print(file_)
        torch.cuda.ipc_collect()
        torch.cuda.empty_cache()
        img = cv2.cvtColor(cv2.imread(filepath), cv2.COLOR_BGR2RGB)
        input_ = torch.from_numpy(img).float().div(255.).permute(2,0,1).unsqueeze(0).cuda()

        # Pad the input if not_multiple_of 4
        h,w = input_.shape[2], input_.shape[3]
        H,W = ((h+img_multiple_of)//img_multiple_of)*img_multiple_of, ((w+img_multiple_of)//img_multiple_of)*img_multiple_of
        padh = H-h if h%img_multiple_of!=0 else 0
        padw = W-w if w%img_multiple_of!=0 else 0
        input_ = F.pad(input_, (0,padw,0,padh), 'reflect')

        restored = model(input_)
        restored = torch.clamp(restored, 0, 1)

        # Unpad the output
        restored = restored[:,:,:h,:w]

        restored = restored.permute(0, 2, 3, 1).cpu().detach().numpy()
        restored = img_as_ubyte(restored[0])
        re = cv2.cvtColor(restored, cv2.COLOR_RGB2BGR)

        filename = os.path.split(filepath)[-1]
        cv2.imwrite(os.path.join(out_dir, filename),cv2.cvtColor(restored, cv2.COLOR_RGB2BGR))
        return jsonify({'filename': filename})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(out_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)