from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail,Message
from sqlalchemy.orm import joinedload, relationship
from sqlalchemy import func, cast, Date, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.orm import sessionmaker





app = Flask(__name__, static_url_path='/static')
bcrypt = Bcrypt(app) 
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///hospital.db'  
app.config['SECRET_KEY']='abc8b193e08abf1df01fdd837'

Base = declarative_base()
engine = create_engine('sqlite:///co.db')  
Session = sessionmaker(bind=engine)
session = Session()


app.config['MAIL_SERVER'] = 'smtp.example.com'  # Set your email server
app.config['MAIL_PORT'] = 587  # Set the port for your email server
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'parasbhosale1543@gmail.com'
app.config['MAIL_PASSWORD'] = 'paras1543'
app.config['MAIL_DEFAULT_SENDER'] = 'parasbosale1543@gmail.com'

db=SQLAlchemy(app) 


app.app_context().push() 
from pythonfiles import route
