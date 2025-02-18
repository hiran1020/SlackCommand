import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
