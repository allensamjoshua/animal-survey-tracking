from flask import Flask, redirect, render_template, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'allen_sam'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc:///?odbc_connect=' +
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-6OI45DP\\SQLEXPRESS;'
    'DATABASE=ut_project;'
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

#homepage 
@app.route('/')
def home():
    return render_template("home.html")

#admin login page
@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        uname = request.form['username']
        pwd = request.form['password']
        admin = Admin.query.filter_by(username=uname)
        if admin and bcrypt.check_password_hash(Admin.password,pwd): #to check if the hashed password matches
            session['admin']==True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Credentials")
    return render_template('admin_login.html')

#admin dashboard page
@app.route('/admin/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
   app.run(debug=True)