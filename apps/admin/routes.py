from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from apps.admin import routes
from apps.jobs.routes import (
    get_all_jobs_with_applicants,
    create_job_from_form,
    update_job_from_form,
    delete_job_with_applicants
)
from apps.authentication.models import User
from apps import db
from datetime import datetime, timedelta
import time, re, random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from apps.admin.models import BaseJob  
from sqlalchemy import text  
admin_blueprint = Blueprint('admin_blueprint', __name__, url_prefix='/admin')
@admin_blueprint.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    from apps.jobs.models import Job
    filters = []

    job_title = request.args.get('job_title', '').strip()
    company_name = request.args.get('company_name', '').strip()
    job_type = request.args.get('job_type', '').strip()
    location = request.args.get('location', '').strip()
    experience = request.args.get('experience', '').strip()

    industry = request.args.get('industry', '').strip()
    if industry:
        filters.append(Job.industry.ilike(f"%{industry}%"))
    if job_title:
        filters.append(Job.job_title.ilike(f"%{job_title}%"))
    if company_name:
        filters.append(Job.company_name.ilike(f"%{company_name}%"))
    if job_type:
        filters.append(Job.job_type.ilike(f"%{job_type}%"))
    if location:
        filters.append(Job.location.ilike(f"%{location}%"))
    if experience:
        filters.append(Job.experience.ilike(f"%{experience}%"))

    jobs = Job.query.filter(*filters).limit(100).all()


    # Gom ứng viên cho từng job
    job_applicants = {}
    from apps.list_seeker.models import ListSeeker
    from apps.authentication.models import User

    for job in jobs:
        applications = ListSeeker.query.filter_by(id_job=job.id_job).all()
        applicants = []
        for app in applications:
            user = User.query.get(app.id_seeker)
            if user:
                applicants.append({
                    'id_user': user.id_user,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone': user.phone,
                    'avatar_file': user.avatar_file,
                    'cv_file': user.cv_file,
                    'apply_time': app.apply_date.strftime('%d %b %H:%M'),
                    'status': app.status
                })
        job_applicants[job.id_job] = {
            'industry': job.industry,  # ✅ thêm dòng này
            'applicants': applicants
        }


    return render_template(
        'admin/dashboard.html',
        jobs=jobs,
        job_applicants=job_applicants
    )

@admin_blueprint.route('/job/add', methods=['GET', 'POST'])
@login_required
def add_job():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        try:
            create_job_from_form(request.form)
            flash("Thêm công việc thành công!", "success")
            return redirect(url_for('admin_blueprint.dashboard'))
        except Exception as e:
            flash("Lỗi khi thêm công việc: " + str(e), "danger")

    return render_template('admin/job_form.html', action='add')

@admin_blueprint.route('/job/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    from apps.jobs.models import Job
    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        try:
            update_job_from_form(job_id, request.form)
            flash("Cập nhật thành công!", "success")
            return redirect(url_for('admin_blueprint.dashboard'))
        except Exception as e:
            flash("Lỗi khi cập nhật công việc: " + str(e), "danger")

    return render_template('admin/job_form.html', action='edit', job=job)
@admin_blueprint.route('/job/delete/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    try:
        delete_job_with_applicants(job_id)
        flash("Đã xoá công việc!", "success")
    except Exception as e:
        flash("Lỗi khi xoá: " + str(e), "danger")

    return redirect(url_for('admin_blueprint.dashboard'))

@admin_blueprint.route('/users')
@login_required
def user_manager():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    username = request.args.get('username', '').strip()
    email = request.args.get('email', '').strip()
    role = request.args.get('role', '').strip()

    filters = []
    if username:
        filters.append(User.username.ilike(f"%{username}%"))
    if email:
        filters.append(User.email.ilike(f"%{email}%"))
    if role:
        filters.append(User.role == role)

    users = User.query.filter(*filters).order_by(User.id_user).all()
    return render_template('admin/user_manager.html', users=users)
@admin_blueprint.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    user = User.find_by_id(user_id)
    if not user:
        flash("Người dùng không tồn tại", "danger")
    elif user.role == 'Admin':
        flash("Không thể xoá tài khoản admin!", "danger")
    else:
        try:
            user.delete_from_db()
            flash("Đã xoá người dùng thành công", "success")
        except Exception as e:
            flash(f"Lỗi khi xoá: {str(e)}", "danger")

    return redirect(url_for('admin_blueprint.user_manager'))
@admin_blueprint.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.date_of_birth = request.form.get('date_of_birth') or None
        user.role = request.form['role']
        db.session.commit()
        flash("Cập nhật thành công!", "success")
        return redirect(url_for('admin_blueprint.user_manager'))

    return render_template('admin/user_form.html', user=user)

@admin_blueprint.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        from werkzeug.security import generate_password_hash
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        date_of_birth = request.form.get('date_of_birth')
        phone = request.form['phone']
        role = request.form['role']

        # Kiểm tra tồn tại
        from apps.authentication.models import User
        if User.query.filter_by(username=username).first():
            flash('Username đã tồn tại.', 'danger')
            return redirect(url_for('admin_blueprint.add_user'))
        if User.query.filter_by(email=email).first():
            flash('Email đã được đăng ký.', 'danger')
            return redirect(url_for('admin_blueprint.add_user'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            date_of_birth=date_of_birth,
            phone=phone,
            role=role
        )

        db.session.add(user)
        db.session.commit()
        flash("Thêm người dùng thành công!", "success")
        return redirect(url_for('admin_blueprint.user_manager'))

    return render_template('admin/user_form.html', action='add')

@admin_blueprint.route('/crawler')
@login_required
def crawler():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403  # Chặn nếu không phải admin
    return render_template('admin/crawler.html')  # Đường dẫn tới template

def normalize(val):
    if val is None:
        return ''
    if isinstance(val, float):
        return str(int(val)) if val.is_integer() else str(round(val, 2))
    return str(val).strip().lower().replace('\xa0', ' ').replace('\n', ' ')

def get_existing_jobs_from_db():
    rows = db.session.execute(
        text("SELECT job_title, company_name, industry, location, salary, experience, create_at FROM base")
    ).fetchall()
    return set(tuple(normalize(col) for col in row[:6]) for row in rows)


def convert_relative_time(time_str):
    if "hôm nay" in time_str.lower():
        return datetime.today().strftime("%Y-%m-%d")
    match = re.search(r'(\d+)\s*(giờ|ngày|tuần|tháng|năm) trước', time_str)
    if match:
        value, unit = int(match.group(1)), match.group(2)
        today = datetime.today()
        if "giờ" in unit:
            return (today - timedelta(hours=value)).strftime("%Y-%m-%d")
        elif "ngày" in unit:
            return (today - timedelta(days=value)).strftime("%Y-%m-%d")
        elif "tuần" in unit:
            return (today - timedelta(weeks=value)).strftime("%Y-%m-%d")
        elif "tháng" in unit:
            return (today - timedelta(days=value * 30)).strftime("%Y-%m-%d")
        elif "năm" in unit:
            return (today - timedelta(days=value * 365)).strftime("%Y-%m-%d")
    return "Không xác định"

@admin_blueprint.route('/admin/do-crawl', methods=['POST'])
@login_required
def do_crawl():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    base_url = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?type_keyword=0&page=1&category_family=r257&sba=1"
    jobs = []
    existing_jobs = get_existing_jobs_from_db()

    VALID_INDUSTRY_KEYWORDS = [
        "Engineer", "Developer", "IT", "Software", "Marketing", "Finance", "Design",
        "Data", "Business", "HR", "Accounting", "Manager", "Sales"
    ]

    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 ...")
    # Nếu muốn chạy ẩn, thêm: options.add_argument("--headless")

    driver = uc.Chrome(options=options)
    driver.get(base_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_items = soup.find_all('div', class_='job-item-search-result')

    for job in job_items:
        try:
            title = job.find('h3', class_='title').get_text(strip=True)
            company_name = job.find('span', class_='company-name').get_text(strip=True)
            location = job.find('span', class_='city-text').get_text(strip=True)
            salary = job.find('label', class_='title-salary')
            salary_text = salary.get_text(strip=True) if salary else "Thỏa thuận"
            experience = job.find('label', class_='exp')
            experience_text = experience.get_text(strip=True) if experience else "Không yêu cầu"
            date_label = job.find('label', class_='address mobile-hidden label-update')
            created_at = convert_relative_time(date_label.get_text(strip=True)) if date_label else datetime.today().strftime("%Y-%m-%d")

            industry_div = job.find('div', class_='tag')
            industries = "Không có thông tin"
            if industry_div:
                tags = [tag.get_text(strip=True) for tag in industry_div.find_all('a', class_='item-tag')
                        if any(k in tag.get_text(strip=True) for k in VALID_INDUSTRY_KEYWORDS)]
                if tags:
                    industries = ', '.join(tags)

            # ✅ Tách từng thành phố nếu có nhiều
            
            for loc in location.split(','):
                loc = loc.strip()
                job_key = (
                    normalize(title),
                    normalize(company_name),
                    normalize(industries),
                    normalize(loc),
                    normalize(salary_text),
                    normalize(experience_text)
                )
                if job_key in existing_jobs:
                    continue  # Bỏ qua nếu đã có

                jobs.append({
                    "job_title": title,
                    "company_name": company_name,
                    "industry": industries,
                    "location": loc,
                    "salary": salary_text,
                    "experience": experience_text,
                    "create_at": created_at
                })


        except Exception as e:
            print("Lỗi khi parse job:", e)
            continue

    driver.quit()
    return render_template('admin/crawler.html', crawled_jobs=jobs)


@admin_blueprint.route('/admin/save-crawled-data', methods=['POST'])
@login_required
def save_crawled_data():
    if session.get('role') != 'Admin':
        return "Unauthorized", 403

    job_count = int(request.form.get('job_count', 0))
    current_date = datetime.utcnow().date()

    for i in range(job_count):
        job = BaseJob(
            job_title=request.form.get(f'job_title_{i}'),
            company_name=request.form.get(f'company_name_{i}'),
            industry=request.form.get(f'industry_{i}'),
            location=request.form.get(f'location_{i}'),
            salary=request.form.get(f'salary_{i}'),
            experience=request.form.get(f'experience_{i}'),
            create_at=current_date
        )
        db.session.add(job)

    db.session.commit()
    return redirect('/admin/crawler')

