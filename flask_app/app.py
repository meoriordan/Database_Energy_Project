import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect, session
from datetime import date

app = Flask(__name__)

app.secret_key = 'my secret key'

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='final_project',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'],
                            )
    return conn


@app.route('/')
def index():
    if 'loggedin' not in session:
        session['loggedin'] = False
    return render_template('index.html', nav_bar = session['loggedin'])

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method=="POST":
        first_name = request.form['fname']
        last_name = request.form['lname']
        username = request.form['uname']
        password = request.form['password']
        conn = get_db_connection() 
        cur = conn.cursor() 
        cur.execute('SELECT max(customer_id) FROM customers;')
        customer_id = cur.fetchall()[0][0]
        customer_id += 1
        print('CUSTOMER IDDDDD: ',customer_id)
        cur.execute('INSERT INTO customers (customer_id, first_name,last_name, username, password)'
            'VALUES(%s, %s, %s, %s, %s)',
            (customer_id,first_name, last_name, username, password))
        conn.commit()
        cur.close()
        conn.close()
    return render_template("signup.html", nav_bar = session['loggedin'])


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form['uname']
        password = request.form['password']
        conn = get_db_connection() 
        cur = conn.cursor() 
        cur.execute('SELECT * FROM customers where username = %s and password = %s',(username, password))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True 
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged In!'
        else:
            msg='Incorrect login info.'
        cur.close()
        conn.close()
        return render_template("login.html", msg=msg, nav_bar = session['loggedin'])
    else:
        return render_template("login.html", nav_bar = session['loggedin'])

@app.route('/logout')
def logout():
    session['loggedin'] = False 
    session['id'] = None
    session['username'] = None
    return redirect(url_for('login'))

@app.route('/locations', methods=('GET','POST'))
def locations():
    if request.method == 'GET':
        if session['loggedin'] == True:
            cust_id = str(session['id'])
            print('cust id issssss(', cust_id,')')
            conn = get_db_connection() 
            cur = conn.cursor() 
            cur.execute('SELECT * FROM locations WHERE customer_id = %s', (cust_id))
            locations = cur.fetchall()
            cur.close()
            conn.close()
            return render_template("locations.html", locations=locations , nav_bar = session['loggedin'])
        else:
            return redirect(url_for('login'))
    elif request.method == 'POST':
        street_num = request.form['street_num']
        street_name = request.form['street_name']
        apt_num = request.form['apt_num']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        num_br = request.form['num_br']
        num_occupants = request.form['num_occupants']
        sqft = request.form['sqft']
        date_added = date.today()
        customer_id = session['id']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT max(location_id) FROM locations;')
        location_id = cur.fetchall()[0][0]
        location_id += 1
        # print('CUSTOMER IDDDDD: ',customer_id)
        cur.execute('INSERT INTO locations (location_id, customer_id,street_num, street_name, apt_num, city, state, zipcode, num_br, num_occupants, sqft, date_added)'
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (location_id, customer_id,street_num, street_name, apt_num, city, state, zipcode, num_br, num_occupants, sqft, date_added))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('locations'))


@app.route('/devices')
def devices():
    if session['loggedin'] == True:
        cust_id = str(session['id'])
        conn = get_db_connection() 
        cur = conn.cursor() 
        cur.execute('SELECT d.* FROM locations l join location_devices ld on l.location_id = ld.location_id join devices d on ld.device_id = d.device_id WHERE customer_id = %s', (cust_id))
        devices = cur.fetchall()
        return render_template("devices.html", devices=devices, nav_bar = session['loggedin'])
    else:
        return redirect(url_for('login'))   



@app.route('/create', methods=('GET','POST'))
def create():
    if request.method == 'POST':
        model = request.form['model']
        device_type = request.form['type']
        description = request.form['description']

        conn = get_db_connection()
        cur = conn.cursor() 
        cur.execute('SELECT max(device_id) FROM devices;')
        device_id = cur.fetchall()[0][0]
        device_id += 1
        cur.execute('INSERT INTO devices (device_id, model, device_type, description)'
                    'VALUES (%s, %s, %s, %s)',
                    (device_id, model, device_type, description))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))  
    return render_template('create.html')