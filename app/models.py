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
    role = db.Column(db.String(32))
    status = db.Column(db.Boolean)
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
            user = Users(username='admin', name_cn='管理员', role=Users.roles.get(1), status=True)
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
            'status': self.status,
            'groups': self.get_user_groups()
        }
        return json_user

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

host_tags = db.Table('host_tags',
                    db.Column('host_id', db.Integer, db.ForeignKey('hosts.id', ondelete='CASCADE')),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'))
)

class Hosts(db.Model):
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64))
    public_ip = db.Column(db.String(15), unique=True)
    local_ip = db.Column(db.String(15), unique=True)
    cpus = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    status = db.Column(db.Boolean)

    system = db.Column(db.Integer,db.ForeignKey('system.id'))
    tags = db.relationship('Tags', backref='host', secondary=host_tags, cascade="all, delete", passive_deletes=True, lazy='dynamic')
    disk = db.relationship('Disks', backref='host', lazy='dynamic')
    
    def to_json(self):
        return {
            'id': self.id,
            'hostname': self.hostname,
            'public_ip': self.public_ip,
            'local_ip': self.local_ip,
            'system': self.system if self.system else '',
            'cpus': self.cpus if self.cpus else '',
            'memory': self.memory if self.memory else '',
            'tags': [ tag.to_json() for tag in self.tags ] if self.tags else '',
            'disk': [ d.to_json() for d in self.disk.all() ] if self.disk.all() else '',
        }
    

class Tags(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    hosts = db.relationship('Hosts', backref='tag', secondary=host_tags, cascade="all, delete", passive_deletes=True, lazy='dynamic')
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Disks(db.Model):
    __tablename__ = 'disks'
    id = db.Column(db.Integer, primary_key=True)
    diskname = db.Column(db.String(12))
    size = db.Column(db.Integer)
    host_id = db.Column(db.Integer,db.ForeignKey('hosts.id'))

    def to_json(self):
        return {
            'diskname': self.diskname,
            'size': self.size
        }

class System(db.Model):
    __tablename__ = 'system'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12))
    img = db.Column(db.String(128))
    host = db.relationship('Hosts', backref='systems', lazy='dynamic')