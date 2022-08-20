import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #for Authorization
    SECRET_KEY = '1a353c04030ed6a1de5501f7d39f5086'

    #DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,'user.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
