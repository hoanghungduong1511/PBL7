from apps.notifications.routes import notifications_blueprint
from flask import Blueprint
# Khởi tạo blueprint cho notifications
notifications_blueprint = Blueprint(
    'notifications_blueprint',  # <== sửa tên nội bộ để khớp
    __name__,
    url_prefix='/notifications'  # giữ nguyên
)
