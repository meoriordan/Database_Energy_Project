import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect, session
from datetime import date
import dotenv

app = Flask(__name__)

app.secret_key = 'my secret key'

dotenv.dotenv_values('.env')


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='final_project',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'],
                            port=5434
                            )
    return conn


@app.route('/')
def index():
    if 'loggedin' not in session:
        session['loggedin'] = False
    return render_template('index.html', nav_bar=session['loggedin'])


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form['fname']
        last_name = request.form['lname']
        username = request.form['uname']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT max(customer_id) FROM customers;')
        customer_id = cur.fetchall()[0][0]
        customer_id += 1
        cur.execute('INSERT INTO customers (customer_id, first_name,last_name, username, password)'
                    'VALUES(%s, %s, %s, %s, %s)',
                    (customer_id, first_name, last_name, username, password))
        conn.commit()
        cur.close()
        conn.close()
    return render_template("signup.html", nav_bar=session['loggedin'])


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['uname']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM customers where username = %s and password = %s', (username, password))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged In!'
        else:
            msg = 'Incorrect login info.'
        cur.close()
        conn.close()
        if account:
            return render_template("index.html", nav_bar=session['loggedin'])
        else:
            return render_template("login.html", msg=msg, nav_bar=session['loggedin'])
    else:
        return render_template("login.html", nav_bar=session['loggedin'])


@app.route('/logout')
def logout():
    session['loggedin'] = False
    session['id'] = None
    session['username'] = None
    return redirect(url_for('login'))


@app.route('/locations/delete/<int:location_id>', methods=['POST'])
def delete_location(location_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM locations WHERE location_id = %s', (location_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('locations'))


@app.route('/locations', methods=('GET', 'POST'))
def locations():
    if request.method == 'GET':
        if session['loggedin']:
            cust_id = str(session['id'])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM locations WHERE customer_id = %s', (cust_id,))
            locations = cur.fetchall()
            cur.close()
            conn.close()
            return render_template("locations.html", locations=locations, nav_bar=session['loggedin'])
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
        if location_id is None:
            location_id = 1
        else:
            location_id += 1

        cur.execute(
            'INSERT INTO locations (location_id, customer_id,street_num, street_name, apt_num, city, state, zipcode, num_br, num_occupants, sqft, date_added)'
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (
                location_id, customer_id, street_num, street_name, apt_num, city, state, zipcode, num_br,
                num_occupants,
                sqft, date_added))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('locations'))


@app.route('/devices/delete/<int:device_enrollment_id>', methods=['POST'])
def delete_devices(device_enrollment_id):
    conn = get_db_connection()
    cur = conn.cursor()
    print('hiii',device_enrollment_id)
    cur.execute('DELETE FROM location_devices WHERE device_enrollment_id = %s', (device_enrollment_id,))
    conn.commit()
    print('hiii',device_enrollment_id)
    cur.close()
    conn.close()
    return redirect(url_for('devices'))


@app.route('/devices', methods=['GET', 'POST'])
def devices():
    if session['loggedin']:
        if request.method == 'GET':
            cust_id = str(session['id'])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT * '
                'FROM locations l join location_devices ld on l.location_id = ld.location_id '
                'join devices d on ld.device_id = d.device_id '
                'WHERE customer_id = %s',
                (cust_id,))

            devices = cur.fetchall()
            cur.execute('SELECT DISTINCT device_type FROM devices')
            types = [i[0] for i in cur.fetchall()]
            cur.execute('SELECT DISTINCT device_type, model FROM devices')
            type_models = cur.fetchall()
            cur.execute('SELECT location_id, street_num, street_name, apt_num, city, state , zipcode '
                        'FROM locations WHERE customer_id = %s', (cust_id,))
            locations = cur.fetchall()

            return render_template("devices.html", devices=devices, types=types, type_models=type_models,
                                   locations=locations, nav_bar=session['loggedin'])
        else:
            model = request.form['model']
            location_id = request.form['location']
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute('SELECT device_id FROM devices WHERE model = %s', (model,))  # should be unique for every model
            (device_id,) = cur.fetchone()

            cur.execute('SELECT max(device_enrollment_id) FROM location_devices;')
            device_enrollment_id = cur.fetchall()[0][0]
            if device_enrollment_id is None:
                device_enrollment_id = 1
            else:
                device_enrollment_id += 1

            cur.execute('INSERT INTO location_devices (device_enrollment_id, location_id, device_id)'
                        'VALUES(%s, %s, %s)',
                        (device_enrollment_id, location_id, device_id))
            conn.commit()
            cur.close()
            conn.close()

            return redirect(url_for('devices'))
    else:
        return redirect(url_for('login'))


@app.route('/create', methods=('GET', 'POST'))
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


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if session['loggedin']:
        cust_id = str(session['id'])
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT DATE_TRUNC('hour', event_occurrence), SUM(value) "
                    "FROM events JOIN location_devices USING (device_enrollment_id) JOIN locations USING (location_id) "
                    "WHERE customer_id=%s AND (event_type = 'energy consumption' OR event_type = 'switch off')"
                    "GROUP BY DATE_TRUNC('hour', event_occurrence)", (cust_id,))
        hourly_sum = cur.fetchall()
        hourly_sum.sort(key=lambda x: x[0])
        print(hourly_sum)

        cur.execute('SELECT device_type, SUM(value) '
                    'FROM events JOIN location_devices USING (device_enrollment_id) JOIN locations USING (location_id) '
                    'JOIN devices USING (device_id) '
                    "WHERE customer_id = %s AND (event_type = 'energy consumption' OR event_type = 'switch off') "
                    'GROUP BY device_type', (cust_id,))
        type_sum_all = cur.fetchall()

        cur.execute('SELECT device_type, SUM(value) '
                    'FROM events JOIN location_devices USING (device_enrollment_id) JOIN locations USING (location_id) '
                    'JOIN devices USING (device_id) '
                    "WHERE customer_id = %s AND (event_type = 'energy consumption' OR event_type = 'switch off') "
                    "AND event_occurrence > NOW() - INTERVAL '30 days'"
                    'GROUP BY device_type', (cust_id,))
        type_sum_30 = cur.fetchall()

        cur.execute('SELECT device_type, SUM(value) '
                    'FROM events JOIN location_devices USING (device_enrollment_id) JOIN locations USING (location_id) '
                    'JOIN devices USING (device_id) '
                    "WHERE customer_id = %s AND (event_type = 'energy consumption' OR event_type = 'switch off') "
                    "AND event_occurrence > NOW() - INTERVAL '7 days'"
                    'GROUP BY device_type', (cust_id,))
        type_sum_7 = cur.fetchall()

        cur.execute("SELECT location_id, sqft, SUM(value) "
                    "FROM events JOIN location_devices USING(device_enrollment_id) JOIN locations USING (location_id) "
                    "WHERE customer_id = %s AND event_occurrence > NOW() - INTERVAL '30 days' AND "
                    "(event_type = 'energy consumption' OR event_type = 'switch off') "
                    "GROUP BY 1, 2", (cust_id,))
        loc_sqft_list = cur.fetchall()
        usage_rank_sqft = []
        for location in loc_sqft_list:
            cur.execute("SELECT location_id, RANK() OVER (ORDER BY SUM(value)) "
                        "FROM events JOIN location_devices USING (device_enrollment_id) "
                        "JOIN locations USING (location_id) "
                        "WHERE sqft BETWEEN %s-50 AND %s+50 "
                        "AND event_occurrence > NOW() - INTERVAL '30 days' AND "
                        "(event_type = 'energy consumption' OR event_type = 'switch off') "
                        "GROUP BY location_id"
                        , (location[1], location[1]))
            similar_sqft = cur.fetchall()
            # (location_id, ranking, length)
            usage_rank_sqft.append(
                (location[0], next(i for i in similar_sqft if i[0] == location[0])[1], len(similar_sqft))
            )

        cur.execute("SELECT location_id, num_occupants, SUM(value) "
                    "FROM events JOIN location_devices USING(device_enrollment_id) JOIN locations USING (location_id) "
                    "WHERE customer_id = %s AND event_occurrence > NOW() - INTERVAL '30 days' AND "
                    "(event_type = 'energy consumption' OR event_type = 'switch off') "
                    "GROUP BY 1, 2", (cust_id,))
        loc_occupants_list = cur.fetchall()
        usage_rank_occupants = []
        for location in loc_occupants_list:
            cur.execute("SELECT location_id, RANK() OVER (ORDER BY SUM(value)) "
                        "FROM events JOIN location_devices USING(device_enrollment_id) "
                        "JOIN locations USING (location_id) "
                        "WHERE num_occupants BETWEEN %s-1 AND %s+1 AND event_occurrence > NOW() - INTERVAL '30 days' AND "
                        "(event_type = 'energy consumption' OR event_type = 'switch off') "
                        "GROUP BY location_id"
                        , (location[1], location[1]))
            similar_occupants = cur.fetchall()
            print(similar_occupants)
            # (location_id, ranking, length)
            usage_rank_occupants.append(
                (location[0], next(i for i in similar_occupants if i[0] == location[0])[1], len(similar_occupants))
            )

        cur.execute('SELECT * FROM locations')
        locations = cur.fetchall()

        return render_template('dashboard.html', nav_bar=session['loggedin'], hourly_sum=hourly_sum,
                               type_sum_all=type_sum_all, type_sum_30=type_sum_30, type_sum_7=type_sum_7,
                               usage_rank_sqft=usage_rank_sqft, locations=locations,
                               usage_rank_occupants=usage_rank_occupants,
                               dates=[i[0].strftime('%-m/%-d/%Y') for i in hourly_sum])
    else:
        return redirect(url_for('login'))
