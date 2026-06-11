from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    activities = db.relationship('Activity', backref='organizer', lazy='dynamic')
    registrations = db.relationship('Registration', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_user


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, nullable=False, default=0)
    registration_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    reject_reason = db.Column(db.String(500))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    registrations = db.relationship('Registration', backref='activity', lazy='dynamic')

    @property
    def current_participants(self):
        return Registration.query.filter_by(activity_id=self.id, status='registered').count()

    @property
    def is_full(self):
        if self.max_participants == 0:
            return False
        return self.current_participants >= self.max_participants


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    status = db.Column(db.String(20), default='registered')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'activity_id'),)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


CATEGORIES = [
    ('sports', '体育运动'),
    ('academic', '学术科研'),
    ('cultural', '文化艺术'),
    ('volunteering', '志愿服务'),
    ('other', '其他'),
]
