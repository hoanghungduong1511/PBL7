from flask import Blueprint, request, jsonify
from apps import db
from apps.notifications.models import Notification
from apps.jobs.models import Job
from flask import jsonify
from flask_login import login_required, current_user
from flask import url_for

# Khởi tạo blueprint cho notifications
notifications_blueprint = Blueprint('notifications_blueprint', __name__, url_prefix='/notifications')

@notifications_blueprint.route('/create', methods=['POST'])
@login_required
def create_notification():
    data = request.get_json()

    user_id = data.get('user_id')     # Người nhận thông báo (HR)
    job_id = data.get('job_id')       # Công việc được ứng tuyển
    type = data.get('type')           # Loại thông báo

    print("[DEBUG] Notification received:", data)

    # Kiểm tra dữ liệu đầu vào
    if not user_id or not job_id or not type:
        print("[ERROR] Missing data: user_id={}, job_id={}, type={}".format(user_id, job_id, type))
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    try:
        # Tạo thông báo với applicant_id là người đang đăng nhập
        notification = Notification(
            user_id=user_id,              # Người nhận (HR)
            job_id=job_id,
            applicant_id=current_user.id_user,  # Người nộp đơn (ứng viên)
            type='new_application',
            status='unread'
        )

        print("[DEBUG] Notification object:", notification)

        db.session.add(notification)
        db.session.commit()

        print("[DEBUG] Notification created successfully")
        return jsonify({'success': True, 'message': 'Notification created successfully'})

    except Exception as e:
        print("[ERROR] Error creating notification:", e)
        return jsonify({'success': False, 'message': str(e)}), 500



# Route lấy thông báo cho người dùng
@notifications_blueprint.route('/get', methods=['GET'])
@login_required
def get_notifications():
    user_id = current_user.id_user
    role = current_user.role  # 'HR' hoặc 'Seeker'

    notifications = Notification.query \
        .filter_by(user_id=user_id) \
        .order_by(Notification.created_at.desc()) \
        .limit(10).all()

    notifications_data = []
    for notif in notifications:
        title = "Thông báo"
        message = "Bạn có một thông báo mới."

        # ✅ Nếu là HR và nhận thông báo có người apply
        if role == 'HR' and notif.type == 'new_application':
            title = "Ứng viên mới"
            message = (
                f"{notif.applicant.full_name} vừa apply vào công việc: {notif.job.job_title}"
                if notif.applicant and notif.job else "Có ứng viên mới ứng tuyển"
            )

        # ✅ Nếu là Seeker và nhận thông báo duyệt/ từ chối
        elif role == 'Seeker':
            if notif.type == 'approved':
                title = "Đơn được duyệt"
                message = (
                    f"🎉 Đơn ứng tuyển của bạn đã được duyệt cho công việc: {notif.job.job_title}"
                    if notif.job else "Đơn đã được duyệt."
                )
            elif notif.type == 'rejected':
                title = "Thông báo: Đơn ứng tuyển bị từ chối"
                message = (
                    f"😞 Rất tiếc! Đơn ứng tuyển của bạn đã bị từ chối cho công việc: {notif.job.job_title}"
                    if notif.job else "Đơn đã bị từ chối."
                )
            else:
                continue  # Nếu seeker mà gặp type khác thì bỏ qua

        else:
            continue  # Nếu HR gặp type không phải 'new_application' thì bỏ qua

        # Avatar: dùng avatar ứng viên nếu có, fallback ảnh mặc định
        avatar = (
            url_for('static', filename=f'uploads/avatar/{notif.applicant.avatar_file}')
            if notif.applicant and notif.applicant.avatar_file
            else url_for('static', filename='assets/images/user/avatar-default.jpg')
        )

        notifications_data.append({
            'id': notif.id_notification,
            'title': title,
            'message': message,
            'created_at': notif.created_at.strftime('%H:%M %d/%m/%Y'),
            'status': notif.status,
            'avatar': avatar,
        })

    return jsonify({'success': True, 'notifications': notifications_data})

# Route đánh dấu thông báo là đã đọc
@notifications_blueprint.route('/mark_read', methods=['POST'])
def mark_notification_read():
    notification_id = request.get_json().get('notification_id')

    if not notification_id:
        return jsonify({'success': False, 'message': 'Notification ID is required'}), 400

    notification = Notification.query.get(notification_id)
    if notification:
        notification.status = 'read'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Notification marked as read'})

    return jsonify({'success': False, 'message': 'Notification not found'}), 404
@notifications_blueprint.route('/clear_all', methods=['POST'])
@login_required
def clear_all_notifications():
    try:
        Notification.query.filter_by(user_id=current_user.id_user).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Đã xoá tất cả thông báo'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
@notifications_blueprint.route('/mark_all_read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    try:
        notifications = Notification.query.filter_by(user_id=current_user.id_user, status='unread').all()
        for notif in notifications:
            notif.status = 'read'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tất cả thông báo đã được đánh dấu là đã đọc'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500