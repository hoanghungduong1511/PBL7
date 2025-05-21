from flask import Blueprint

admin_blueprint = Blueprint(
    'admin_blueprint',
    __name__,
    url_prefix='/admin',
    template_folder='templates'
)

from apps.admin import routes
