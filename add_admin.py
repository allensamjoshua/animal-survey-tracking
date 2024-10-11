from flask import Flask, request, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

admin_app = Flask(__name__)

admin_app.config['SECRET_KEY'] = '6HE6W43I1'
admin_app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc:///?odbc_connect=' +
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-NP4U7J0\\SQLEXPRESS;'
    'DATABASE=ut_project;'
    'Trusted_Connection=yes;'
)

db = SQLAlchemy(admin_app)
bcrypt = Bcrypt(admin_app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(60), nullable=False)

@admin_app.route('/', methods = ['GET','POST'])
def admin_signup():
    if request.method == 'POST':
        uname = request.form['username']
        e_id = request.form['email']
        pwd = request.form['password']

        hashed_pwd = bcrypt.generate_password_hash(pwd).decode('utf-8')
        admin_add = Admin(username = uname, email = e_id, password = hashed_pwd)

        db.session.add(admin_add)
        db.session.commit()
        flash("Admin Created")
            
    return render_template("create_admin.html")

if __name__ == '__main__':
    admin_app.run(debug=True)