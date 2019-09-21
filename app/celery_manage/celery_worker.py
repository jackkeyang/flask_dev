from app import create_app, celery
import os

application = create_app('dev')
application.app_context().push()

if __name__ == '__main__':
    application.run()