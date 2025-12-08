This is a full-stack web application designed for travel and tourism enthusiasts. Built using Python (Flask), MySQL, and HTML/CSS, the platform allows users to search and book hotels and flights across India. It features a user panel for searching and managing bookings, and an admin panel to manage hotels, flights, and overall bookings.
install dependencies: pip install -r requirements.txt (in bash)
Setup MySQL database: Run tourism.sql
Update config (Open config.py and set your MySQL credentials):
MYSQL_HOST = 'localhost'
MYSQL_USER = 'your_username'
MYSQL_PASSWORD = 'your_password'
MYSQL_DB = 'tourism'
Run the Flask app: python app.py (in bash)
Register with an account and make it admin in MySQL: update users set is_admin=1 where email = 'your_email';
