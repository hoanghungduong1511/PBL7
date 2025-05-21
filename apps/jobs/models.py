from apps import db
from sqlalchemy.exc import SQLAlchemyError

class Job(db.Model):
    __tablename__ = 'jobs'

    id_job = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.String(100))
    experience = db.Column(db.String(100))
    deadline = db.Column(db.Date, nullable=False)
    id_hr = db.Column(db.Integer, db.ForeignKey('user.id_user'))

    industry = db.Column(db.String(100))  # ✅ Thêm dòng này

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(">>> DB Error:", e)
