from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3 as sql
import os
import random
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


app = Flask(__name__)

# File Upload Configuration
UPLOAD_FOLDER = "static/files"
FILE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "tblr3398@gmail.com"
SENDER_PASSWORD = "lvhi qlvd ztbv aaoi"


app.secret_key = 'admin123'

# Check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in FILE_EXTENSIONS

# Validate email format
def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

# @app.route("/")
# def index():
#     con = sql.connect("db_web.db")
#     con.row_factory = sql.Row
#     cur = con.cursor()
#     cur.execute("SELECT * FROM users")
#     data = cur.fetchall()
#     con.close()
#     return render_template("index.html", datas=data)

# @app.route("/add_user", methods=['POST', 'GET'])
# def add_user():
#     if request.method == 'POST':
#         uname = request.form['uname']
#         contact = request.form['contact']
#         email = request.form['email']
#         password = request.form['password']
#         profile_pic = request.files['profile_pic']
#         profile_pic_filename = None

#         if not is_valid_email(email):
#             flash('Invalid email format', 'danger')
#             return redirect(url_for("add_user"))

#         hashed_password = generate_password_hash(password)

#         if profile_pic and allowed_file(profile_pic.filename):
#             filename, file_extension = os.path.splitext(profile_pic.filename)
#             profile_pic_filename = secure_filename(filename + str(random.randint(10000, 99999)) + file_extension)
#             profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_filename))

#         con = sql.connect("db_web.db")
#         cur = con.cursor()
#         try:
#             cur.execute("INSERT INTO users (UNAME, CONTACT, EMAIL, PASSWORD, PROFILE_PIC) VALUES (?, ?, ?, ?, ?)", 
#                         (uname, contact, email, hashed_password, profile_pic_filename))
#             con.commit()
#             flash('User Added Successfully', 'success')
#         except sql.IntegrityError:
#             flash('Email already exists!', 'danger')
#         finally:
#             con.close()

#         return redirect(url_for("index"))

#     return render_template("add_user.html")


# Send Email Notification
def send_email_notification(to_email, username):
    subject = "Welcome to Our Platform!"
    body = f"Hello {username},\n\nThank you for registering. Your account has been successfully created.\n\nBest Regards,\nYour Team"
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route("/")
def index():
    con = sql.connect("db_web.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    con.close()
    return render_template("index.html", datas=data)

@app.route("/add_user", methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        uname = request.form['uname']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']
        profile_pic = request.files['profile_pic']
        profile_pic_filename = None

        if not is_valid_email(email):
            flash('Invalid email format', 'danger')
            return redirect(url_for("add_user"))

        hashed_password = generate_password_hash(password)

        if profile_pic and allowed_file(profile_pic.filename):
            filename, file_extension = os.path.splitext(profile_pic.filename)
            profile_pic_filename = secure_filename(filename + str(random.randint(10000, 99999)) + file_extension)
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_filename))

        con = sql.connect("db_web.db")
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO users (UNAME, CONTACT, EMAIL, PASSWORD, PROFILE_PIC) VALUES (?, ?, ?, ?, ?)", 
                        (uname, contact, email, hashed_password, profile_pic_filename))
            con.commit()
            flash('User Added Successfully', 'success')
            send_email_notification(email, uname)  # Send email after adding user
        except sql.IntegrityError:
            flash('Email already exists!', 'danger')
        finally:
            con.close()

        return redirect(url_for("index"))

    return render_template("add_user.html")


@app.route("/verify_user/<string:uid>", methods=['GET', 'POST'])
def verify_user(uid):
    if request.method == 'POST':
        password = request.form['password']
        
        con = sql.connect("db_web.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT PASSWORD FROM users WHERE UID=?", (uid,))
        user = cur.fetchone()
        con.close()

        if user and check_password_hash(user["PASSWORD"], password):
            session['edit_user_id'] = uid
            return redirect(url_for("edit_user", uid=uid))
        else:
            flash("Incorrect password. Try again.", "danger")

    return render_template("verify_user.html", uid=uid)

@app.route("/edit_user/<string:uid>", methods=['POST', 'GET'])
def edit_user(uid):
    if 'edit_user_id' not in session or session['edit_user_id'] != uid:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("index"))

    con = sql.connect("db_web.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    
    if request.method == 'POST':
        uname = request.form['uname']
        contact = request.form['contact']
        email = request.form['email']
        profile_pic = request.files['profile_pic']
        profile_pic_filename = request.form['existing_profile_pic']

        if not is_valid_email(email):
            flash('Invalid email format', 'danger')
            return redirect(url_for("edit_user", uid=uid))

        if profile_pic and allowed_file(profile_pic.filename):
            filename, file_extension = os.path.splitext(profile_pic.filename)
            profile_pic_filename = secure_filename(filename + str(random.randint(10000, 99999)) + file_extension)
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_filename))

        cur.execute("UPDATE users SET UNAME=?, CONTACT=?, EMAIL=?, PROFILE_PIC=? WHERE UID=?", 
                    (uname, contact, email, profile_pic_filename, uid))
        con.commit()
        con.close()
        
        session.pop('edit_user_id', None)
        flash('User Updated Successfully', 'success')
        return redirect(url_for("index"))

    cur.execute("SELECT * FROM users WHERE UID=?", (uid,))
    data = cur.fetchone()
    con.close()
    return render_template("edit_user.html", datas=data)

@app.route("/delete_user/<string:uid>", methods=['GET'])
def delete_user(uid):
    con = sql.connect("db_web.db")
    cur = con.cursor()
    
    cur.execute("SELECT PROFILE_PIC FROM users WHERE UID=?", (uid,))
    profile_pic = cur.fetchone()[0]
    if profile_pic:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic))

    cur.execute("DELETE FROM users WHERE UID=?", (uid,))
    con.commit()
    con.close()
    
    flash('User Deleted Successfully', 'warning')
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)