import os

basedir = os.path.abspath(os.path.dirname(__file__))
#for Authorization
SECRET_KEY = ''

#DB
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,'user.db')
