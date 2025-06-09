from apps import db
from datetime import date

class BaseJob(db.Model):
    __tablename__ = 'base'

    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.String(100))
    experience = db.Column(db.String(100))
    create_at = db.Column(db.Date, default=date.today, nullable=False)

    def __repr__(self):
        return f"<BaseJob {self.job_title} - {self.company_name}>"
