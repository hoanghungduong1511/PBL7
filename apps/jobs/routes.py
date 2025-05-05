from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from apps import db
from apps.jobs.models import Job

jobs_blueprint = Blueprint('jobs_blueprint', __name__)

@jobs_blueprint.route('/post_job', methods=['POST'])
@login_required
def post_job():

    try:
        job = Job(
            job_title=request.form['job_title'],
            company_name=request.form['company_name'],
            job_type='online',
            location=request.form['location'],
            salary=request.form.get('salary'),
            experience=request.form.get('experience'),
            deadline=datetime.strptime(request.form['deadline'], '%Y-%m-%d'),
            id_hr=current_user.id_user
        )
        job.save()
        flash("Đăng bài thành công", "success")
    except Exception as e:
        print(">>> Exception:", e)
        flash("Lỗi đăng bài: " + str(e), "danger")

    return redirect(url_for('home_blueprint.index'))
from datetime import date
from apps.list_seeker.models import ListSeeker

@jobs_blueprint.route('/apply_job/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    print(">>> Apply Job ID:", job_id)
    try:
        new_apply = ListSeeker(
            id_job=job_id,
            id_seeker=current_user.id_user,
            status='applied',
            apply_date=date.today()
        )
        db.session.add(new_apply)
        db.session.commit()
        flash("Ứng tuyển thành công!", "success")
    except Exception as e:
        db.session.rollback()
        print(">>> Apply Error:", e)
        flash("Có lỗi khi ứng tuyển: " + str(e), "danger")

    return redirect(url_for('home_blueprint.index'))

