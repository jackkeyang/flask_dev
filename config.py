from datetime import timedelta

class Config:
    SECRET_KEY = '0LAFvVAbcufUX1SVNSaRBCp2PgIqVVz4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:123456@172.16.10.11:3306/flask_ops?charset=utf8'
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERYBEAT_SCHEDULE = {
        'host_ping': {
            'task': 'host_ping',
            'schedule': timedelta(seconds=30)
        },
        'host_info': {
            'task': 'host_info',
            'schedule': timedelta(seconds=60)
        }
    }

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:123456@172.16.10.11:3306/flask_ops?charset=utf8'

config = {
    'dev': DevelopmentConfig,
    'pro': ProductionConfig,
    'default': DevelopmentConfig
}
