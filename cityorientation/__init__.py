from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
app.config['SECRET_KEY'] = '50d2d80ebd0f26be1720f1565182f6ef'
app.config['UPLOAD_FOLDER'] = 'quest_images/'
db_client = MongoClient('localhost', 27027)
db = db_client['city_orientation']
db_quests = db['quests']
db_teams = db['teams']
db_templates = db['templates']
db_tasks = db['tasks']
db_stat = db['stat']
timezone = -3 * 60 * 60

from cityorientation import routes, rest_api, settings
