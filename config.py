class Config:
    SECRET_KEY = '0LAFvVAbcufUX1SVNSaRBCp2PgIqVVz4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:123456@172.16.10.11:3306/flask_ops?charset=utf8'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:123456@172.16.10.11:3306/flask_ops?charset=utf8'

config = {
    'dev': DevelopmentConfig,
    'pro': ProductionConfig,
    'default': DevelopmentConfig
}