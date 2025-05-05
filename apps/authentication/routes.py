# -*- encoding: utf-8 -*-
"""
Authentication Routes (Login / Logout / Register) - sử dụng bảng 'user' chuẩn hóa
"""

from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_user, logout_user
from flask_dance.contrib.github import github
from flask_dance.contrib.google import google

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import User
from apps.config import Config
from werkzeug.security import check_password_hash, generate_password_hash

# ------------------------------
# Github login
# ------------------------------
@blueprint.route("/github")
def login_github():
    if not github.authorized:
        return redirect(url_for("github.login"))
    github.get("/user")  # You can handle user info here if needed
    return redirect(url_for('home_blueprint.index'))

# ------------------------------
# Google login
# ------------------------------
@blueprint.route("/google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    google.get("/oauth2/v1/userinfo")
    return redirect(url_for('home_blueprint.index'))

# ------------------------------
# Login (username hoặc email)
# ------------------------------
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if request.method == 'POST':
        

        if login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data


            user = User.find_by_username(username) or User.find_by_email(username)
            if not user:
                print(">>> User not found.")
                flash('Unknown User or Email', 'danger')
                return render_template('authentication/login.html', form=login_form)
            

            
            password_check = check_password_hash(user.password_hash,password)
            

            if password_check:
                login_user(user)
                print(current_user.is_authenticated)
                print(current_user.full_name)
                print(current_user.email)
                print(">>> ✅ login_user DONE")
                return redirect(url_for('home_blueprint.index'))
            else:
                print(">>> ❌ Wrong password")
                flash('Wrong username/email or password', 'danger')
                return render_template('authentication/login.html', form=login_form)
        else:
            print(">>> ❌ Form validation failed")

    if not current_user.is_authenticated:
        return render_template('authentication/login.html', form=login_form)
    
    return redirect(url_for('home_blueprint.index'))

# ------------------------------
# Register (Tạo user mới)
# ------------------------------
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)

    if request.method == 'POST' and create_account_form.validate_on_submit():
        username = create_account_form.username.data
        email = create_account_form.email.data
        password = create_account_form.password.data
        full_name = create_account_form.full_name.data
        date_of_birth = create_account_form.date_of_birth.data
        phone = create_account_form.phone.data
        role = create_account_form.role.data

        # Kiểm tra username hoặc email đã tồn tại chưa
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('authentication/register.html', form=create_account_form)

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('authentication/register.html', form=create_account_form)

        # Tạo user mới
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            date_of_birth=date_of_birth,
            phone=phone,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully.', 'success')
        return redirect(url_for('authentication_blueprint.login'))

    return render_template('authentication/register.html', form=create_account_form)

# ------------------------------
# Logout
# ------------------------------
@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))

# ------------------------------
# Context processors (Social login)
# ------------------------------
@blueprint.context_processor
def has_github():
    return {'has_github': bool(Config.GITHUB_ID) and bool(Config.GITHUB_SECRET)}

@blueprint.context_processor
def has_google():
    return {'has_google': bool(Config.GOOGLE_ID) and bool(Config.GOOGLE_SECRET)}

# ------------------------------
# Unauthorized handler (nếu chưa login mà vào page cần login)
# ------------------------------
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('authentication_blueprint.login'))
