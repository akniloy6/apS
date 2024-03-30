from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from . import db
from .model import Image, User
import os

views = Blueprint('views', __name__)

# @views.route('/home', methods=['GET', 'POST'])
# @login_required
# def home():
#     # if request.method == 'POST':
#     #     file_ = request.files['image']
#     #     file_name = file_.filename
#     #     file_.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
#     #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
#     #     # Call your prediction function here
#     #     flash('Photo uploaded successfully', category='success')
#     return render_template('home.html', current_user=current_user)

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
            if file_.filename == '':
                flash('No file selected', category='error')
            else:
                print('File uploaded')
                selected_option = request.form.get('processing_option')
                if selected_option:
                    # Process the image based on the selected option
                    if selected_option == 'lowLight':
                        # Process image for low light enhancement
                        print('Low light enhancement')
                    elif selected_option == 'improveResolution':
                        # Process image to improve resolution
                        print('Improve resolution', selected_option)
                    elif selected_option == 'denoise':
                        # Process image to de-noise
                        print('De-noise')

                    # Flash message indicating successful upload and processing
                    flash('Image processed successfully', category='success')
                else:
                    flash('No processing option selected', category='error')

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
