import os
base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = '6de1bc827fb03e7be8ac70c3bd060f7b'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(base_dir, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
