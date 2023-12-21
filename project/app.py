from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Initialize the database
conn = sqlite3.connect('hotel_booking.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact_number TEXT,
        room_number INTEGER,
        check_in DATE,
        check_out DATE
    )
''')
conn.commit()
conn.close()

# Routes
@app.route('/')
def index():
    today = datetime.now().date()
    return render_template('index.html', today=today)

@app.route('/bookings')
def bookings():
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings ORDER BY check_in')
    data = cursor.fetchall()
    conn.close()
    return render_template('bookings.html', bookings=data)

@app.route('/create_booking', methods=['POST'])
def create_booking():
    name = request.form.get('name')
    contact_number = request.form.get('contact_number')
    room_number = int(request.form.get('room_number'))
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')

    # Convert date strings to datetime objects
    check_in_date = datetime.strptime(check_in, '%d-%m-%Y')
    check_out_date = datetime.strptime(check_out, '%d-%m-%Y')

    # Check if the dates are in the future
    today = datetime.now().date()
    if (
        check_in_date.date() < today
        or check_out_date.date() <= today
        or check_in_date.date() >= check_out_date.date()
    ):
        return "Invalid date selection. Please choose future dates and ensure check-out is after check-in."

    # Check if the room is available
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE room_number = ? AND check_in < ? AND check_out > ?', (room_number, check_out_date, check_in_date))
    conflicting_bookings = cursor.fetchall()
    conn.close()

    if conflicting_bookings:
        return f"Room {room_number} is not available for the selected dates."

    # Book the room
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bookings (name, contact_number, room_number, check_in, check_out) VALUES (?, ?, ?, ?, ?)',
                   (name, contact_number, room_number, check_in_date, check_out_date))
    conn.commit()
    conn.close()

    return redirect(url_for('create_booking'))

@app.route('/edit_booking/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    if request.method == 'GET':
        conn = sqlite3.connect('hotel_booking.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        booking = cursor.fetchone()
        conn.close()

        if not booking:
            return "Booking not found."

        return render_template('edit_booking.html', booking=booking)

    elif request.method == 'POST':
        name = request.form.get('name')
        contact_number = request.form.get('contact_number')
        room_number = int(request.form.get('room_number'))
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')

        # Convert date strings to datetime objects
        check_in_date = datetime.strptime(check_in, '%d-%m-%Y')
        check_out_date = datetime.strptime(check_out, '%d-%m-%Y')

        # Check if the dates are in the future
        today = datetime.now().date()
        if (
            check_in_date.date() < today
            or check_out_date.date() <= today
            or check_in_date.date() >= check_out_date.date()
        ):
            return "Invalid date selection. Please choose future dates and ensure check-out is after check-in."

        # Check if the room is available
        conn = sqlite3.connect('hotel_booking.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE room_number = ? AND check_in < ? AND check_out > ? AND id != ?', (room_number, check_out_date, check_in_date, booking_id))
        conflicting_bookings = cursor.fetchall()
        conn.close()

        if conflicting_bookings:
            return f"Room {room_number} is not available for the selected dates."

        # Update the booking
        conn = sqlite3.connect('hotel_booking.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE bookings SET name=?, contact_number=?, room_number=?, check_in=?, check_out=? WHERE id=?', (name, contact_number, room_number, check_in, check_out, booking_id))
        conn.commit()
        conn.close()

        return redirect(url_for('bookings'))

@app.route('/delete_booking/<int:booking_id>')
def delete_booking(booking_id):
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('bookings'))

if __name__ == '__main__':
    app.run(debug=True)
