import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Set up database location and secret key for later
class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "devPass"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False