# app/__init__.py

# import os
from flask import Flask


# Initialize the app
app = Flask(__name__, instance_relative_config=True)

# app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

# Load the views
from app import views

# Load the config file
app.config.from_object('config')
