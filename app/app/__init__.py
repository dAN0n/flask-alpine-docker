from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import basedir
import os

# Application instance
app = Flask(__name__)
# Application configuration
app.config.from_object('config')
# Application database
db = SQLAlchemy(app)
# Application database migrations
migrate = Migrate(app, db)

# Close the database session after each request or application context shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Import views (must be after the application object is created)
from app import rest, views, models, FtsRequest

# Register blueprint Receipt-Analyzer v1.0
app.register_blueprint(rest.RAv1)