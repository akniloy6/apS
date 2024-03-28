from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .model import Image, User
import os

views = Blueprint('views', __name__)

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # if request.method == 'POST':
    #     file_ = request.files['image']
    #     file_name = file_.filename
    #     file_.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
    #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    #     # Call your prediction function here
    #     flash('Photo uploaded successfully', category='success')
    return render_template('home.html')

@views.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'signup' in request.form:
            return redirect('/signup')
        elif 'login' in request.form:
            return redirect('/login')
    return render_template('index.html')

