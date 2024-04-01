from flask_sqlalchemy import SQLAlchemy
from flask import Flask, send_from_directory
import os
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "image_restorer.db"

app = Flask(__name__, static_folder='/image_restorer/static', static_url_path='/image_restorer/static')

def create_app():
    app.config['SECRET_KEY'] = 'xxcc3344'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = '/image_restorer/static/images/uploads/'
    app.config['OUTPUT_FOLDER'] = '/image_restorer/static/images/restored/'

    app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
    
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    from .model import User, Image
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    with app.app_context():
        db.create_all()
    
    return app

def create_database(app):
    if not os.path.exists('db/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/restored/<filename>')
def restored_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
