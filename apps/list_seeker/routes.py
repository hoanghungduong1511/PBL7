from flask import Blueprint, render_template, session, jsonify, request
from flask_login import login_required, current_user
from apps.jobs.models import Job
from apps.list_seeker.models import ListSeeker
from apps.authentication.models import User
from apps import db
from apps.notifications.models import Notification



list_seeker_blueprint = Blueprint('list_seeker_blueprint', __name__)

@list_seeker_blueprint.route('/view_applicants/<int:job_id>')
@login_required
def view_applicants(job_id):
    print("Đã gọi hàm", current_user.id_user)
    if session.get('role') != 'HR':
        return "Unauthorized", 403

    # Kiểm tra job có thuộc về HR hiện tại không
    job = Job.query.filter_by(id_job=job_id, id_hr=current_user.id_user).first()
    if not job:
        return "Không tìm thấy bài đăng phù hợp", 403

    applications = ListSeeker.query.filter_by(id_job=job_id).all()

    applicants = []
    for app in applications:
        seeker = User.query.get(app.id_seeker)
        if seeker and seeker.role == 'seeker':
            applicants.append({
                'id_user': seeker.id_user,
                'full_name': seeker.full_name,
                'email': seeker.email,
                'phone': seeker.phone,
                'avatar_file': seeker.avatar_file,
                'cv_file': seeker.cv_file,
                'apply_time': app.apply_date.strftime('%d %b %H:%M'),
                'status': app.status
            })
            print("SEEKER ID:", seeker.id_user)
            print("AVATAR FILE:", seeker.avatar_file)
            print("CV FILE:", seeker.cv_file)

    return render_template(
        'hr_role/view_applicants_modal.html',
        job=job,
        job_applicants={job.id_job: applicants}
    )


@list_seeker_blueprint.route('/update_applicant_status', methods=['POST'])
@login_required
def update_applicant_status():
    data = request.get_json()
    print("Data received:", data)

    try:
        seeker_id = int(data.get('list_seeker_id'))
        job_id = int(data.get('job_id'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid ID format'}), 400

    status = data.get('status')

    if not seeker_id or not status or not job_id:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    if status not in ['approved', 'rejected']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    seeker = ListSeeker.query.filter_by(id_seeker=seeker_id, id_job=job_id).first()
    if not seeker:
        return jsonify({'success': False, 'message': 'Application not found'}), 404

    print(f"Current status for seeker {seeker_id} and job {job_id}: {seeker.status}")
    seeker.status = status
    print(f"Updated status for seeker {seeker_id} and job {job_id}: {seeker.status}")

    try:
        # ✅ Tạo thông báo cho người apply
        notification = Notification(
            user_id=seeker_id,              # người nhận là ứng viên
            job_id=job_id,
            applicant_id=current_user.id_user,  # HR là người duyệt
            type=status,                   # 'approved' hoặc 'rejected'
            status='unread'
        )
        db.session.add(notification)

        db.session.commit()
        return jsonify({'success': True, 'new_status': status})
    except Exception as e:
        db.session.rollback()
        print("Error committing to DB:", e)
        return jsonify({'success': False, 'message': 'Database update failed'}), 500
