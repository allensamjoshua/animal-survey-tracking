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
    place = db.Column(db.String(50))
    location = db.Column(db.String(50), nullable=False)
    animal_count = db.Column(db.Integer)
    survey_date = db.Column(db.Date)
    surveyor_name = db.Column(db.String(50))
    method = db.Column(db.String(50))
    status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Homepage 
@app.route('/', methods=['GET'])
def home():
    query = request.args.get('query', '')  # Get the search query from the URL
    results = []
    
    if query:
        results = AnimalSurvey.query.filter(AnimalSurvey.location.ilike(f'%{query}%')).all()
    
    return render_template("home.html", results=results, query=query)

# Admin login page
@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        admin = Admin.query.filter_by(username=uname).first()
        if admin and bcrypt.check_password_hash(admin.password, pwd):  # Check if the hashed password matches
            session['admin'] = True  # Set session variable upon successful login
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Credentials")
    return render_template('admin_login.html')

# Admin dashboard page
@app.route('/admin/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    animals = AnimalSurvey.query.all()
    return render_template('admin_dashboard.html', animals=animals)

@app.route('/admin/admin_dashboard/create_record', methods=['GET','POST'])
def create_record():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        s_id = request.form['survey_id']
        a_name = request.form['animal_name']
        plc = request.form['place']
        loc = request.form['location']
        a_count = request.form['animal_count']
        s_date = request.form['survey_date']
        s_name = request.form['surveyor_name']
        s_type = request.form['type']
        stats = request.form['status']
        notes = request.form['notes']

        exist = AnimalSurvey.query.filter_by(survey_id=s_id).first()
        if exist:
            flash("Survey Id already exists!")
            return redirect(url_for('admin_dashboard'))
        
        else:
            insert_qry = AnimalSurvey(
                survey_id=s_id,
                animal_name=a_name,
                place = plc,
                location=loc,
                animal_count=a_count,
                survey_date=s_date,
                surveyor_name=s_name,
                method = s_type,
                status=stats,
                notes=notes
            )

            db.session.add(insert_qry)
            db.session.commit()
            flash("New Record Added")
            return redirect(url_for('admin_dashboard'))
  
    return render_template('create_record.html')

@app.route('/admin/admin_dashboard/update_record/<int:survey_id>', methods=['GET', 'POST'])
def update_record(survey_id):
    if "admin" not in session:
        return redirect(url_for('admin_login'))
    
    exists = AnimalSurvey.query.filter_by(survey_id=survey_id).first()
    
    if request.method == 'POST':
        if exists:
            # Update fields if provided
            if request.form['animal_name']:
                exists.animal_name = request.form['animal_name']

            if request.form['place']:
                exists.place = request.form['place']

            if request.form['location']:
                exists.location = request.form['location']

            if request.form['animal_count']:
                exists.animal_count = request.form['animal_count']

            if request.form['survey_date']:
                exists.survey_date = request.form['survey_date']

            if request.form['surveyor_name']:
                exists.surveyor_name = request.form['surveyor_name']

            if request.form['status']:
                exists.status = request.form['status']

            if request.form['notes']:
                exists.notes = request.form['notes']
            
            db.session.commit()
            flash("Updated the record")
            return redirect(url_for('admin_dashboard'))
        
        flash("Record does not exist")
        return redirect(url_for('admin_dashboard'))

    # For GET request, render the form with existing data
    if exists:
        return render_template('update_record.html', animal=exists)
    
    flash("Record does not exist")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/admin_dashboard/delete_record/<int:survey_id>", methods=['GET', 'POST'])
def delete_record(survey_id):
    if "admin" not in session:
        return redirect(url_for('admin_login'))
    
    record = AnimalSurvey.query.filter_by(survey_id=survey_id).first()
    
    if record:
        db.session.delete(record)
        db.session.commit()
        flash("Deleted Record Successfully!")
    
    return redirect(url_for("admin_dashboard"))

@app.route('/admin/admin_dashboard/logout', methods=['GET'])
def logout():
    session.pop('admin', None)  # Remove the admin session
    return redirect(url_for('home'))  # Redirect to the homepage or login page

if __name__ == '__main__':
   app.run(debug=True)