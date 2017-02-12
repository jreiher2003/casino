import os 
from flask import Flask 
# from flask_mongoalchemy import MongoAlchemy 


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
# db = MongoAlchemy(app)

from app import views 