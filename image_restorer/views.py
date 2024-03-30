import os
from . import db
from .model import Image, User
from .restorer import prediction
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in 'ALLOWED_EXTENSIONS'

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    user_uploaded_images = Image.query.filter_by(uploader=current_user.id).all()
    image_names = [image.name for image in user_uploaded_images]
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file uploaded', category='error')
        else:
            file_ = request.files['image']
            print('File:', file_.filename)
            if file_.filename == '':
                flash('No file selected', category='error')
            elif file_ and file_.filename != '':
                    print('File is allowed')
                    file_name = secure_filename(file_.filename)
                    print('Secured filename:', file_name)
                    file_path = os.path.join('static', 'images', 'uploads', file_name)
                    file_.save(file_path)
                    print('File path:', file_path)
                    # Create new image instance and add to database
                    new_image = Image(name=file_name, uploader=current_user.id, image_path=file_path)
                    db.session.add(new_image)
                    db.session.commit()
                    
                    restored_image_path = prediction(file_path)
                    print(restored_image_path)
                # TODO: Send the file to prediction function defined in restorer.py
                # TODO: Display the actual image and the restored image
                    return render_template('home.html', current_user=current_user, image_names=image_names, actual_image=file_path, restored_image=restored_image_path)
            else:
                flash('File type not allowed', category='error')
    return render_template('home.html', current_user=current_user, image_names=image_names)

@views.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        if 'signup' in request.form:
            return redirect('/signup')
        elif 'login' in request.form:
            return redirect('/login')
    return render_template('index.html')

@views.route('/', methods=['GET', 'POST'])
def index():
    return render_template('landing_page.html')
