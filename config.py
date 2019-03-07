class Config:
    SECRET_KEY = '0LAFvVAbcufUX1SVNSaRBCp2PgIqVVz4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:123456@192.168.2.100:3306/devops?charset=utf8'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:123456@localhost:3306/devops?charset=utf8'

config = {
    'dev': DevelopmentConfig,
    'pro': ProductionConfig,
    'default': DevelopmentConfig
}