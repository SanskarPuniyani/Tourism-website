from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import datetime
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# MySQL Configuration
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        flash('Registration successful! Please log in.')
        return redirect('/login')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user and check_password_hash(user['password'], password_input):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect('/')
        else:
            flash('Incorrect email or password')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Search Hotels and Flights
@app.route('/search', methods=['GET', 'POST'])
def search():
    hotels = []
    flights = []
    if request.method == 'POST':
        city = request.form['city']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM hotels WHERE city=%s", (city,))
        hotels = cur.fetchall()

        cur.execute("SELECT * FROM flights WHERE from_city=%s OR to_city=%s", (city, city))
        flights = cur.fetchall()
    return render_template('search.html', hotels=hotels, flights=flights)

# Booking Form
@app.route('/book/<booking_type>/<int:item_id>', methods=['GET', 'POST'])
def book(booking_type, item_id):
    if 'loggedin' not in session:
        return redirect('/login')

    if request.method == 'POST':
        num_people = int(request.form['num_people'])
        checkin_date = request.form.get('checkin_date')  # For hotel booking
        checkout_date = request.form.get('checkout_date')  # For hotel booking
        flight_date = request.form.get('flight_date')  # For flight booking

        cur = mysql.connection.cursor()

        if booking_type == 'hotel':
            cur.execute("INSERT INTO bookings (user_id, booking_type, booking_id, num_people, checkin_date, checkout_date, booking_date) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (session['id'], booking_type, item_id, num_people, checkin_date, checkout_date, datetime.date.today()))
        else:  # Flight booking
            cur.execute("INSERT INTO bookings (user_id, booking_type, booking_id, num_people, flight_date, booking_date) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (session['id'], booking_type, item_id, num_people, flight_date, datetime.date.today()))

        mysql.connection.commit()
        flash('Booking successful!')
        return redirect('/bookings')

    return render_template('booking_form.html', booking_type=booking_type, item_id=item_id)

# Booking History
@app.route('/bookings')
def bookings():
    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM bookings WHERE user_id=%s", (session['id'],))
    bookings = cur.fetchall()

    enriched_bookings = []
    for b in bookings:
        if b['booking_type'] == 'hotel':
            cur.execute("SELECT * FROM hotels WHERE id=%s", (b['booking_id'],))
        else:
            cur.execute("SELECT * FROM flights WHERE id=%s", (b['booking_id'],))
        item = cur.fetchone()
        b['details'] = item
        enriched_bookings.append(b)

    return render_template('bookings.html', bookings=enriched_bookings)

@app.route('/admin/hotels', methods=['GET', 'POST'])
def admin_add_hotel():
    if not session.get('is_admin'):
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        price = request.form['price']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO hotels (name, city, price_per_night) VALUES (%s, %s, %s)", (name, city, price))
        mysql.connection.commit()
        flash('Hotel added successfully')
    return render_template('admin_add_hotel.html')

@app.route('/admin/flights', methods=['GET', 'POST'])
def admin_add_flight():
    if not session.get('is_admin'):
        return redirect('/')
    if request.method == 'POST':
        flight_name = request.form['flight_name']
        from_city = request.form['from_city']
        to_city = request.form['to_city']
        price = request.form['price']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO flights (flight_name, from_city, to_city, price) VALUES (%s, %s, %s, %s)",
                    (flight_name, from_city, to_city, price))
        mysql.connection.commit()
        flash('Flight added successfully')
    return render_template('admin_add_flight.html')

@app.route('/admin/bookings')
def admin_bookings():
    if not session.get('is_admin'):
        return redirect('/')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM bookings")
    bookings = cur.fetchall()
    return render_template('admin_bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)
