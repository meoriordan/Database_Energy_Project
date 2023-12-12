import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="final_project",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'],
        port=5434)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS books;')


# Insert data into the table

cur.execute('DROP TABLE IF EXISTS events;')
cur.execute('DROP TABLE IF EXISTS location_devices;')
cur.execute('DROP TABLE IF EXISTS locations;')
cur.execute('DROP TABLE IF EXISTS customers;')
cur.execute('DROP TABLE IF EXISTS devices;')
cur.execute('DROP TABLE IF EXISTS energy_costs;')

cur.execute('CREATE TABLE customers(customer_id SERIAL PRIMARY KEY,'
            'first_name VARCHAR(50) NOT NULL,'
            'last_name VARCHAR(50) NOT NULL,'
            'username VARCHAR(50) NOT NULL UNIQUE,'
            'password VARCHAR(50) NOT NULL);')

cur.execute('INSERT INTO customers (customer_id,first_name,last_name, username, password)'
            'VALUES(%s, %s, %s, %s, %s)',
            (1,'John','Smith','jsmith','noodle'))

cur.execute('CREATE TABLE locations(location_id SERIAL PRIMARY KEY,'
    'customer_id INTEGER NOT NULL,'
    'street_num INTEGER NOT NULL,'
    'street_name VARCHAR(50) NOT NULL,'
    'apt_num INTEGER,'
    'city VARCHAR(50) NOT NULL,'
    'state CHAR(2) NOT NULL,'
    'zipcode INTEGER NOT NULL,'
    'num_br INTEGER NOT NULL,'
    'num_occupants INTEGER NOT NULL,'
    'sqft INTEGER NOT NULL,'
    'date_added DATE NOT NULL,'
    'FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE);'
)

cur.execute('CREATE TABLE devices(device_id SERIAL PRIMARY KEY,'
    'model VARCHAR(100) NOT NULL,'
    'device_type VARCHAR(50) NOT NULL,'
    'description VARCHAR(200));')

cur.execute('INSERT INTO devices (device_id,model, device_type, description)'
            'VALUES(%s, %s, %s, %s)',
            (1, 'Cosmo 22 cu ft 4-door French Door Refrigerator','refrigerator','french door refrigerator easy to clean; led lighting'))

cur.execute('INSERT INTO devices (device_id,model, device_type, description)'
            'VALUES(%s, %s, %s, %s)',
            (2, 'Frididaire 18.3 cu ft Top Freezer Refrigerator','refrigerator','spacious interior storage; keep produce fresh longer'))

cur.execute('INSERT INTO devices (device_id,model, device_type, description)'
            'VALUES(%s, %s, %s, %s)',
            (3, 'Electrolux 27 in W 4.5 cu ft Front Load Washer with SmartBoost','washer','most effective washer; keep whites whiter; remove detergent residues'))

cur.execute('INSERT INTO devices (device_id,model, device_type)'
            'VALUES(%s, %s, %s)',
            (4, 'Electrolux 4.5 cu ft Stackable Front Load Washer','washer'))

cur.execute('INSERT INTO devices (device_id,model, device_type, description)'
            'VALUES(%s, %s, %s, %s)',
            (5, 'Kasa Smart Light Bulb KL110r','smart light','Dimmable Kasa Smarts dimmable light bulb; No hub required'))


cur.execute('INSERT INTO devices (device_id,model, device_type, description)'
            'VALUES(%s, %s, %s, %s)',
            (6, 'Proctor Silex 2-Slice Toaster','toaster','EFFORTLESSLY TOAST THICKER BREADS; EASILY RETRIEVE SMALLER SIZED BREADS'))



cur.execute('CREATE TABLE location_devices(device_enrollment_id SERIAL PRIMARY KEY,'
    'location_id INTEGER NOT NULL,'
    'device_id INTEGER NOT NULL,'
    'FOREIGN KEY(location_id) REFERENCES locations(location_id) ON DELETE CASCADE,'
    'FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE);')

cur.execute('CREATE TABLE events(device_enrollment_id INTEGER NOT NULL,'
    'event_type VARCHAR(50) NOT NULL,'
    'value NUMERIC(10,8),'
    'event_occurrence TIMESTAMP NOT NULL,'
    'PRIMARY KEY(device_enrollment_id, event_type, event_occurrence),'
    'FOREIGN KEY (device_enrollment_id) REFERENCES location_devices(device_enrollment_id) ON DELETE CASCADE);')

cur.execute('CREATE TABLE energy_costs('
    'zip_code INTEGER NOT NULL,'
    'valid_from TIMESTAMP NOT NULL,'
    'valid_to TIMESTAMP,'
    'cost NUMERIC(8,2) NOT NULL,'
    'PRIMARY KEY(zip_code, valid_from));')


conn.commit()

cur.close()
conn.close()