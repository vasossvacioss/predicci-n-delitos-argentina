import os
from flask import Flask

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

from . import routes
