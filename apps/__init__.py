# -*- encoding: utf-8 -*-
"""
App Init - cấu hình Flask app
"""

import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

# Khởi tạo SQLAlchemy và LoginManager
db = SQLAlchemy()
login_manager = LoginManager()

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

def register_blueprints(app):
    for module_name in ('authentication', 'home', 'dyn_dt', 'charts', 'jobs'):
        module = import_module(f'apps.{module_name}.routes')
        app.register_blueprint(module.jobs_blueprint if module_name == 'jobs' else module.blueprint)

def create_app(config):
    # Cấu hình thư mục tĩnh và template
    static_prefix = '/static'
    templates_dir = os.path.dirname(config.BASE_DIR)

    TEMPLATES_FOLDER = os.path.join(templates_dir, 'templates')
    STATIC_FOLDER = os.path.join(templates_dir, 'static')

    print(' > TEMPLATES_FOLDER: ' + TEMPLATES_FOLDER)
    print(' > STATIC_FOLDER:    ' + STATIC_FOLDER)

    app = Flask(__name__, static_url_path=static_prefix,
                template_folder=TEMPLATES_FOLDER,
                static_folder=STATIC_FOLDER)

    app.config.from_object(config)

    register_extensions(app)
    register_blueprints(app)

    return app
