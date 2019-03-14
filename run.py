from flask_script import Manager, Shell
from app import create_app
from flask_migrate import Migrate, MigrateCommand
from app import db
from app.models import *
import os

app = create_app(os.getenv('env'))
migrate = Migrate(app, db)
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db)

@manager.command
def db_deploy():
    Users.insert_user()

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()