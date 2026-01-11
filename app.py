# Import Useful libraries
import flask_login
import sms as sms
from flask_mysqldb import MySQL
import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, app, jsonify
import re, requests
import MySQLdb.cursors
from database import Database
from user import User
import json
import datetime
from datetime import timedelta
import ast
from flask_wtf.csrf import CSRFProtect, CSRFError
import time
import random
import smtplib, ssl
from email.message import EmailMessage
from argon2 import PasswordHasher
import OpenSSL
import certifi


# global Vars
app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
#database = Database()
app.secret_key = "ming"
#app.config['SECRET_KEY'] = "ming"
app.config['MYSQL_HOST'] = 'awsdatabase.co0i3lykfqxy.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin' #change to root
app.config['MYSQL_PASSWORD'] = 'Pa$$w0rd' #change to Pa$$w0rd
app.config['MYSQL_DB'] = 'pythonlogin'
mysql = MySQL(app)



#@app.route('/')
@app.route("/index")
def index():
    print('hi')
    if 'loggedin' in session:
        print("hi")
        return render_template("index.html")
    return redirect(url_for('login'))

#NEED REEEEEEEEEEEEEEE
@app.route("/display", methods=['post','get'])
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #account = database.getUserbyName(session['username'])
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = cursor.execute('select * from accounts where username = %s and password = %s and email = %s', (username, password, email))
        mysql.connection.commit()
        return render_template("display.html", cursor=cursor)
    return redirect(url_for('login'))

# Starting page which will be displayed to user when app is started
@app.route('/', methods=['GET', 'POST'])
def login():
    #ph = PasswordHasher()
    # Message to be displayed
    msg = ''
    sitekey = "6Lc9JPYgAAAAAMxcrs-LwhfRXbK-yKNhh8ae-VTu"
    # Check is the call is post and fields are not empty
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        #account = database.getUser(username, password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()


        # start session  If account exist otherwise display the message
        try:
            if account['password'] == password:
                session['loggedin'] = True
                session['username'] = account['username']
                msg = 'Logged in successfully !'
                return render_template('index.html', msg=msg)

            if account['password'] != password:
                session['loggedin'] = False
                session['username'] = account['username']
                msg = 'Please re password!'
                return render_template('login.html', msg=msg, siteky=sitekey)
        except:
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            # Fetch one record and return result
            account = cursor.fetchone()
            flash("Please do the CAPTCHA")


            cursor.execute('UPDATE accounts set logincount = %s where id = %s;', (newaccountlogincount,account['id']))
            #cursor.execute(account['logincount']=newaccountlogincount)
            mysql.connection.commit()


            msg = 'Incorrect username or Password'

    return render_template('login.html', msg=msg, siteky=sitekey)

# Function to signout the user when clicked
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Function to use for Registring the element
@app.route('/register', methods=['GET', 'POST'])
def register():
    handStor=[]
    logincount='0'
    msg = ''
    # Check if the call is post and fields are not empty
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print("hi")

        # Check if user with that username already exist
        #account = database.getUser(username, password)
        #if account:
        ###user = authy_api.users.create(email=email, phone=phoneNO, country_code=countrycode)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        account = cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        if cursor.execute('select * from accounts where username = %s and password = %s', (username, password,)):
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            #database.AddUser(User(username, password, gender, email, country))
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #authyid = user.id
            authyid=0
            cursor.execute("insert into `accounts` (`id`, `username`, `password`, `email`) values (NULL, %s, %s, %s);", (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            #msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    ph=PasswordHasher()
    if 'loggedin' in session:
        if request.method == 'POST' and 'password' in request.form:
            password = ph.hash(request.form['password'])
            username = session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("Update accounts set password = %s where username = %s",(password,username))
            mysql.connection.commit()
            msg = 'You have successfully updated !'
            return render_template("login.html")
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg=msg)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))
    #database.CloseDatabase(debug=True)



