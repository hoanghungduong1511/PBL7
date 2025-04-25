# -*- encoding: utf-8 -*-
"""
Authentication Models - chuẩn hóa với bảng 'user' trong MySQL
"""

from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin


from apps import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Admin', 'HR', 'Seeker'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id_user)if self.id_user else None
    

    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id_user': self.id_user,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'phone': self.phone
        }

    @classmethod
    def find_by_email(cls, email: str):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username: str):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id_user=_id).first()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise IntegrityError(error, 422)

    def delete_from_db(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise IntegrityError(error, 422)
        return

# Flask-Login user loader
@login_manager.user_loader
def user_loader(user_id):
    return User.query.filter_by(id_user=user_id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    return User.query.filter_by(username=username).first()


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id_user", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User")
