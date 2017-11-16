import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None or os.environ.get('DATABASE_URL') is "":
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = False

JSON_AS_ASCII = False
ERROR_404_HELP = False
CSRF_ENABLED = True

SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_MASK_SWAGGER = False

if os.environ.get('FLASK_APP_SECRET_KEY') is None or os.environ.get('FLASK_APP_SECRET_KEY') is "":
    SECRET_KEY = 'FU8vYvAvQB3q8XVrtPFcjcSbv'
else:
    SECRET_KEY = os.environ['FLASK_APP_SECRET_KEY']