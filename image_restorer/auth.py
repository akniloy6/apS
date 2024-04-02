from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .model import User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully", category="success")
                login_user(user, remember=True)
                print("User is logged in: ", current_user)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password", category="error")
        else:
            flash("Email does not exist", category="error")
    return render_template("index.html")


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "success")
    return redirect(url_for("views.index"))


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already exists", category="error")
        elif len(email) < 15:
            flash("Email must be greater than 15 characters.", category="error")
        elif len(full_name) < 2:
            flash("Name must be greater than 3 character.", category="error")
        elif len(password) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            new_user = User(
                email=email,
                full_name=full_name,
                password=generate_password_hash(
                    password, method="pbkdf2", salt_length=16
                ),
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            return redirect(url_for("auth.login"))
    return render_template("index.html")
