# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import Email, DataRequired, Length, InputRequired

# login and registration

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    full_name = StringField('Full Name', validators=[InputRequired()])
    date_of_birth = DateField('Date of Birth', validators=[InputRequired()], format='%Y-%m-%d')
    phone = StringField('Phone Number', validators=[InputRequired()])
    role = SelectField('Role', choices=[('HR', 'Người Tuyển Dụng'), ('Seeker', 'Người Tìm Kiếm Việc Làm')], validators=[InputRequired()])
