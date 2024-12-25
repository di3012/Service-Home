# config.py
import os

class Config:
    SECRET_KEY = '5303'  # Replace with a real secret key in production

    # Get the absolute path to the directory of this config file
    basedirpath = os.path.abspath(os.path.dirname(__file__))
    basedir =  os.path.abspath(os.path.dirname(basedirpath))
    # Create the full absolute path to your database file
    database_path = os.path.join(basedir, 'instance', 'home_service.db')
    # database_path = 'D:/IITM project/MAD-1/House_app_V1/Services@home/instance/home_service.db'

    SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_path}'  # Use SQLite for a simple setup; change as needed
    SQLALCHEMY_TRACK_MODIFICATIONS = False
