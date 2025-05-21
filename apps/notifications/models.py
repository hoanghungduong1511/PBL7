from apps import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id_notification = db.Column(db.Integer, primary_key=True)

    # Người nhận thông báo (HR)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)

    # Công việc liên quan
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id_job'), nullable=False)

    # Người nộp đơn (ứng viên)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=True)

    type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='unread')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # Liên kết với các bảng liên quan
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('received_notifications', lazy=True))
    job = db.relationship('Job', backref=db.backref('notifications', lazy=True))
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref=db.backref('applied_notifications', lazy=True))

    def __repr__(self):
        return f"<Notification {self.type} | Job {self.job_id} | From {self.applicant_id}>"
