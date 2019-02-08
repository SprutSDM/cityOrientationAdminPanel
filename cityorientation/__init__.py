from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = '50d2d80ebd0f26be1720f1565182f6ef'

from cityorientation import routes, settings

