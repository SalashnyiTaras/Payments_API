from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from payments.extensions import csrf

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = 'SecretKey01'
db = SQLAlchemy(app)

from payments import routes
