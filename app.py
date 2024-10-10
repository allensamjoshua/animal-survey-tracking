from flask import Flask, redirect, render_template, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import random
import smtplib
from email.message import EmailMessage

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
    email = db.Column(db.String(60), nullable = False, unique = True)

class Requests(db.Model):
    req_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50), nullable = False)
    phn_no = db.Column(db.Integer, nullable = False)
    email = db.Column(db.String(100), nullable = False)
    district = db.Column(db.String(50), nullable = False)
    state = db.Column(db.String(50), nullable = False)
    status = db.Column(db.String(50), nullable = False, default='pending...')
    details = db.Column(db.Text, nullable = False)

#Home Page
@app.route('/', methods=['GET'])
def home():
    query = request.args.get('query', '')  # Get the search query from the URL
    results = []
    
    if query:
        results = AnimalSurvey.query.filter(AnimalSurvey.location.ilike(f'%{query}%')).all()
    
    return render_template("home.html", results=results, query=query)

@app.route('/request_page', methods=['GET','POST'])
def request_page():
    if request.method == "POST":
        uname = request.form['u_name']
        ph_no = request.form['ph_no']
        email = request.form['email']
        district = request.form['dist']
        state = request.form['state']
        det = request.form['details']

        insert_qry = Requests(
            name = uname,
            phn_no = ph_no,
            email = email,
            district = district,
            state = state,
            details = det
        )


        db.session.add(insert_qry)
        db.session.commit()
        session['sending'] = insert_qry.id
        flash("Request Sent! We will get back to you shortly!")
        return redirect(url_for("home"))

    return render_template('request_page.html')

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

@app.route("/admin/forgot", methods=['GET','POST'])
def getemail():
    if request.method == 'POST':
        e_id = request.form['email']

        exist = Admin.query.filter_by(email=e_id).first()

        if exist:
            def generate_otp():
                otp = random.randint(100000, 999999) #generates random six digit number
                return otp

            def send_otp(otp, receiver_email):
                sender_email = "allensamjoshua2003@gmail.com"
                sender_password = "qbhu pwzo fnxg ydyh" #gmail app password

                msg = EmailMessage() 
                msg.set_content(f"Your OTP for password recovery is: {otp}\nNEVER SHARE THIS WITH ANYONE!")
                msg['Subject'] = "OTP for Password Recovery"
                msg['From'] = sender_email
                msg['To'] = receiver_email

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp: #465 port number used for SSL-Encrypted email communication
                    smtp.login(sender_email, sender_password)
                    smtp.send_message(msg)

            otp = generate_otp()
            send_otp(otp, e_id) #calling the function
            
            session['otp'] = otp  # Store OTP in session
            session['email'] = e_id  # Store email in session 
            flash("OTP sent to your email.")
            return redirect(url_for('validateotp'))

        else:
            flash("Invalid email.")
            
    return render_template('enter_email.html')


@app.route('/admin/forgot/validateotp', methods=['GET', 'POST'])
def validateotp():
    if request.method == 'POST':
        otp = request.form['otp']
        
        if 'otp' in session and str(session['otp']) == otp:
            return redirect(url_for('newpwd'))  # OTP is correct, redirect to password reset
        else:
            flash("Invalid OTP.")
            return redirect(url_for('getemail'))

    return render_template('enter_otp.html')

@app.route('/admin/forgot/validate/otp/enter_password', methods=['GET', 'POST'])
def newpwd():
    if request.method == 'POST':
        pwd = request.form['new_password']
        cpwd = request.form['confirm_password']

        if pwd == cpwd:
            hashed_pwd = bcrypt.generate_password_hash(pwd).decode('utf-8')
            admin = Admin.query.filter_by(email=session.get('email')).first()  # Fetch admin by stored email

            if admin:
                admin.password = hashed_pwd
                db.session.commit()
                flash("Password changed successfully.")
                session.pop('otp', None)  # Clear OTP from session
                return redirect(url_for('admin_login'))
        else:
            flash("Passwords do not match.")
    
    return render_template('enter_password.html')

# Admin dashboard page
@app.route('/admin/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    animals = AnimalSurvey.query.all()
    return render_template('admin_dashboard.html', animals=animals)

@app.route('/admin/admin_request_page', methods=['GET', 'POST'])
def admin_requests():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    reqs = Requests.query.all()
    return render_template("admin_request_page.html", reqs = reqs)

@app.route('/admin/admin_request_page/completed_survey/<int:req_id>/<string:email>', methods=['GET', 'POST'])
def completed_survey(req_id, email):
    if "admin" not in session:
        return redirect(url_for('home'))

    exist = Requests.query.filter_by(req_id=req_id).first()
    if request.method == 'POST':

        if exist:
            exist.status = "Survey Conducted!"
            db.session.commit()         

            def send_mail(receiver_email):
                sender_email = "allensamjoshua2003@gmail.com"
                sender_password = "qbhu pwzo fnxg ydyh"  # Gmail app password

                msg = EmailMessage()
                msg.set_content(f"Hello Solider, We received your survey request and we are glad to accept your request and conduct the survey. Kindly check our website for the survey of your request!")
                msg['Subject'] = "Survey Conducted"
                msg['From'] = sender_email
                msg['To'] = receiver_email

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(sender_email, sender_password)
                    smtp.send_message(msg)

            send_mail(email)  # calling the function
    return redirect(url_for('admin_dashboard'))  # Redirect to a valid page after sending the email

@app.route('/admin/admin_request_page/decline_survey/<int:req_id>/<string:email>', methods=['GET', 'POST'])
def decline_survey(req_id, email):
    if "admin" not in session:
        return redirect(url_for("admin_dashboard"))

    exists = Requests.query.filter_by(req_id=req_id).first()
    
    if request.method == 'POST':
        if exists:
            exists.status = "Request Declined"
            db.session.commit()

            def send_mail(receiver_email):
                sender_email = "allensamjoshua2003@gmail.com"
                sender_password = "qbhu pwzo fnxg ydyh"  # Gmail app password

                msg = EmailMessage()
                msg.set_content(f"Hello Solider, We recieved your survey request but unfortunately we cannot move on with your request. Thank you for contacting us!")
                msg['Subject'] = "Survey Request Declined"
                msg['From'] = sender_email
                msg['To'] = receiver_email

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(sender_email, sender_password)
                    smtp.send_message(msg)

            send_mail(email)  # calling the function
    return redirect(url_for('admin_dashboard'))  # Redirect to a valid page after sending the email

@app.route('/admin/admin_request_page/delete_request/<int:req_id>', methods=['GET', 'POST'])
def delete_request(req_id):
    if "admin" not in session:
        return redirect(url_for('admin_login'))
    
    exist = Requests.query.filter_by(req_id = req_id).first()

    if exist:
        db.session.delete(exist)
        db.session.commit()
        flash("Request Deleted")

        return redirect(url_for("admin_requests"))
    
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