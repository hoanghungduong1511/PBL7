# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import json
import os
import time
import wtforms
from flask import render_template, request, redirect, url_for, flash, current_app, send_file, abort
from io import BytesIO
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from jinja2 import TemplateNotFound

from apps.home import blueprint
from apps import db
from apps.models import get_jobs, count_jobs
from apps.tasks import *
from apps.authentication.models import User as User

from flask_wtf import FlaskForm





# ------------------------------
@blueprint.route('/')
@blueprint.route('/index')
def index():
    # Lấy các tham số lọc
    experience = request.args.get('experience', '').strip()
    position = request.args.get('position', '').strip().lower()
    job_type = request.args.get('job_type', '').strip().lower()
    location = request.args.get('location', '').strip().lower()
    page = int(request.args.get('page', 1))
    per_page = 9
    offset = (page - 1) * per_page

    is_filtering = any([experience, position, job_type, location])

    if is_filtering:
        # Nếu đang tìm kiếm → không phân trang, trả về tất cả job khớp
        jobs = get_jobs(0, 1000, experience, position, job_type, location)
        page = 1
        total_pages = 1
    else:
        # Mặc định có phân trang
        jobs = get_jobs(offset, per_page, experience, position, job_type, location)
        total = count_jobs(experience, position, job_type, location)
        total_pages = (total + per_page - 1) // per_page

    return render_template(
        'pages/index.html',
        segment='index',
        jobs=jobs,
        page=page,
        total_pages=total_pages
    )




# ------------------------------
# Các trang tĩnh giữ nguyên
# ------------------------------
@blueprint.route('/icon_feather')
def icon_feather():
    return render_template('pages/icon-feather.html', segment='icon_feather')

@blueprint.route('/color')
def color():
    return render_template('pages/color.html', segment='color')

@blueprint.route('/sample_page')
def sample_page():
    return render_template('pages/sample-page.html', segment='sample_page')

@blueprint.route('/typography')
def typography():
    return render_template('pages/typography.html', segment='typography')

# ------------------------------
# Trang Profile (giữ nguyên)
# ------------------------------
@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Tạo form để chỉnh sửa thông tin
    class ProfileForm(FlaskForm): pass

    # Danh sách các trường không cho phép sửa (readonly_fields)
    readonly_fields = ['password_hash', 'role']  # Thêm các trường bạn muốn khóa chỉnh sửa

    # Tạo các trường form từ model User
    for column in User.__table__.columns:
        if column.name == "id_user":  # Không cho phép sửa id_user
            continue
        field_name = column.name
        if field_name in readonly_fields:
            continue  # Không tạo form field cho các trường readonly
        field = getField(column)
        setattr(ProfileForm, field_name, field)

    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Lưu các trường không phải readonly
        for field_name, field_value in form.data.items():
            if field_name not in readonly_fields:
                setattr(current_user, field_name, field_value)

        db.session.commit()
        flash('Thông tin đã được cập nhật thành công!', 'success')
        return redirect(url_for('home_blueprint.profile'))

    context = {
        'segment': 'profile',
        'form': form,
        'readonly_fields': readonly_fields
    }
    return render_template('pages/profile.html', **context)


# ------------------------------
# Helper: Get WTForms field from SQLAlchemy type
# ------------------------------
def getField(column):
    if isinstance(column.type, db.Text):
        return wtforms.TextAreaField(column.name.title())
    if isinstance(column.type, db.String):
        return wtforms.StringField(column.name.title())
    if isinstance(column.type, db.Boolean):
        return wtforms.BooleanField(column.name.title())
    if isinstance(column.type, db.Integer):
        return wtforms.IntegerField(column.name.title())
    if isinstance(column.type, db.Float):
        return wtforms.DecimalField(column.name.title())
    if isinstance(column.type, db.LargeBinary):
        return wtforms.HiddenField(column.name.title())
    return wtforms.StringField(column.name.title())






# ------------------------------
# Trang lỗi & xử lý lỗi
# ------------------------------
@blueprint.route('/error-403')
def error_403():
    return render_template('error/403.html'), 403

@blueprint.errorhandler(403)
def not_found_error(error):
    return redirect(url_for('error-403'))

@blueprint.route('/error-404')
def error_404():
    return render_template('error/404.html'), 404

@blueprint.errorhandler(404)
def not_found_error(error):
    return redirect(url_for('error-404'))

@blueprint.route('/error-500')
def error_500():
    return render_template('error/500.html'), 500

@blueprint.errorhandler(500)
def not_found_error(error):
    return redirect(url_for('error-500'))


# ------------------------------
# Celery test route
# ------------------------------
@blueprint.route('/tasks-test')
def tasks_test():
    input_dict = { "data1": "04", "data2": "99" }
    input_json = json.dumps(input_dict)
    task = celery_test.delay(input_json)
    return f"TASK_ID: {task.id}, output: { task.get() }"



# Route cập nhật profile (tải lên tệp CV và Avatar)
import os
from werkzeug.utils import secure_filename
from flask import flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from apps import db

# Định nghĩa các kiểu file được phép
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Kiểm tra xem file có hợp lệ không (dựa vào phần mở rộng file)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





# Route cập nhật profile (tải lên tệp CV và Avatar)
@blueprint.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    # Đảm bảo các thư mục uploads/cv và uploads/avatar tồn tại
    upload_dir_cv = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cv')
    upload_dir_avatar = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatar')

    if not os.path.exists(upload_dir_cv):
        os.makedirs(upload_dir_cv)

    if not os.path.exists(upload_dir_avatar):
        os.makedirs(upload_dir_avatar)

    if request.method == 'POST':
        # Lấy các trường văn bản từ form
        username = request.form.get('username')  # Không thay đổi username
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date_of_birth = request.form.get('date_of_birth')  # Lấy ngày sinh từ form
        
        # Lấy các file từ form
        cv_file = request.files.get('cv_file')
        avatar_file = request.files.get('avatar_file')

        print("Starting file upload process...")  # Kiểm tra nếu code vào được đây

        # Lưu file CV nếu có
        if cv_file and allowed_file(cv_file.filename):
            filename = secure_filename(cv_file.filename)
            file_path = os.path.join(upload_dir_cv, filename)  # Lưu vào uploads/cv

            # Kiểm tra và xóa CV cũ nếu có
            if current_user.cv_file and os.path.exists(os.path.join(upload_dir_cv, current_user.cv_file)):
                os.remove(os.path.join(upload_dir_cv, current_user.cv_file))  # Xóa CV cũ
                print(f"Old CV file removed: {current_user.cv_file}")

            cv_file.save(file_path)
            current_user.cv_file = filename  # Cập nhật tên CV mới vào DB
            print(f"CV file uploaded: {file_path}")  # Kiểm tra nếu tệp CV được lưu
            flash(f"CV file uploaded: {file_path}", 'success')  # Thông báo thành công
        else:
            flash("No CV file uploaded or file type not allowed", 'danger')  # Thông báo lỗi
            print("No valid CV file uploaded.")  # Kiểm tra lỗi

        # Lưu file Avatar nếu có
        if avatar_file and allowed_file(avatar_file.filename):
            filename = secure_filename(avatar_file.filename)
            file_path = os.path.join(upload_dir_avatar, filename)  # Lưu vào uploads/avatar

            # Kiểm tra và xóa Avatar cũ nếu có
            if current_user.avatar_file and os.path.exists(os.path.join(upload_dir_avatar, current_user.avatar_file)):
                os.remove(os.path.join(upload_dir_avatar, current_user.avatar_file))  # Xóa Avatar cũ
                print(f"Old Avatar file removed: {current_user.avatar_file}")

            avatar_file.save(file_path)
            current_user.avatar_file = filename  # Cập nhật tên Avatar mới vào DB
            print(f"Avatar file uploaded: {file_path}")  # Kiểm tra nếu tệp Avatar được lưu
            flash(f"Avatar file uploaded: {file_path}", 'success')  # Thông báo thành công
        else:
            flash("No Avatar file uploaded or file type not allowed", 'danger')  # Thông báo lỗi
            print("No valid Avatar file uploaded.")  # Kiểm tra lỗi

        # Cập nhật các thông tin khác
        current_user.full_name = full_name
        current_user.email = email
        current_user.phone = phone
        current_user.date_of_birth = date_of_birth  # Cập nhật ngày sinh
        print(f"Updating User Info - Full Name: {full_name}, Email: {email}, Phone: {phone}, Date of Birth: {date_of_birth}")

        db.session.commit()  # Lưu thông tin vào cơ sở dữ liệu
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('home_blueprint.profile'))  # Quay về trang profile của người dùng

    return render_template('update_profile.html')  # Trả về trang profile nếu không phải POST






@blueprint.route('/view_avatar')
@login_required
def view_avatar():
    # Kiểm tra nếu người dùng có avatar
    if current_user.avatar_file:
        # Lấy đường dẫn đầy đủ tới tệp avatar
        avatar_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatar', current_user.avatar_file)
        try:
            # Trả về file ảnh avatar
            return send_file(avatar_file_path)
        except Exception as e:
            flash('Error while retrieving avatar.', 'danger')
            return redirect(url_for('authentication_blueprint.profile'))
    else:
        # Nếu không có avatar, hiển thị ảnh mặc định
        default_avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatar', 'default_avatar.jpg')
        return send_file(default_avatar_path)



@blueprint.route('/view_cv')
@login_required
def view_cv():
    # Kiểm tra nếu người dùng có CV
    if current_user.cv_file:
        # Lấy đường dẫn đầy đủ tới tệp CV
        cv_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cv', current_user.cv_file)
        try:
            # Trả về file CV dưới dạng PDF để trình duyệt hiển thị
            return send_file(cv_file_path, mimetype='application/pdf')
        except Exception as e:
            flash('Error while retrieving your CV.', 'danger')
            return redirect(url_for('authentication_blueprint.profile'))
    else:
        flash('No CV uploaded.', 'warning')
        return redirect(url_for('authentication_blueprint.profile'))


