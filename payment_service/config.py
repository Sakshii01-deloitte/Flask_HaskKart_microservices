import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'payment.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    discounts={
        "DISCOUNT5":0.05,
        "DISCOUNT10":0.1
    }