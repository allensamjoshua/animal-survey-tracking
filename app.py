from flask import Flask, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'allen_sam'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc:///?odbc_connect=' +
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-6OI45DP\\SQLEXPRESS;'
    'DATABASE=project_ut;'
    'Trusted_Connection=yes;'
)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class AnimalSurvey(db.Model):
    survey_id = db.Column(db.Integer, primary_key=True)
    animal_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    animal_count = db.Column(db.Integer)
    survey_date = db.Column(db.Date)
    sureyor_name = db.Column(db.String(50))
    status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/a')
def admin_login():
    pass

if __name__ == '__main__':
    app.run(debug=True)