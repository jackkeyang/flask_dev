#coding=utf8
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from . import login_manager

group_users = db.Table('group_user',
                        db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

class Users(UserMixin, db.Model):
    roles = {
             1: 'ADMIN',
             2: 'USER'
            }
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    name_cn = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    role = db.Column(db.String(64))
    group_id = db.relationship('Group', secondary=group_users, backref='users')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def insert_user():
        user = Users.query.filter_by(username='admin').first()
        if user is None:
            user = Users(username='admin', name_en='管理员', role=Users.roles.get(1))
            user.password = '123456'
            db.session.add(user)
            db.session.commit()

    def getnerate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return Users.query.get(data['id'])

    def get_user_groups(self):
        groups = self.group_id
        gs = {}
        if groups:
            for g in groups:
                gs[g.id] = g.name
        return gs

    def to_json(self):
        json_user = {
            'id': self.id,
            'username': self.username,
            'name_cn': self.name_cn,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'groups': self.get_user_groups()
        }
        return json_user

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


