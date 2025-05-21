# apps/list_seeker/models.py

from apps import db

class ListSeeker(db.Model):
    __tablename__ = 'list_seeker'

    id_list = db.Column(db.Integer, primary_key=True)
    id_job = db.Column(db.Integer, db.ForeignKey('jobs.id_job'))
    id_seeker = db.Column(db.Integer, db.ForeignKey('user.id_user'))
    status = db.Column(db.Enum('applied', 'approved', 'rejected'), default='applied')
    apply_date = db.Column(db.Date)
