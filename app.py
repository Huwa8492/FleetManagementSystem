from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key='secret_key_for_flash'

#Connect to the database
def get_db_connection():
    conn = sqlite3.connect('fleet.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()

    vehicles=conn.execute('SELECT * FROM Vehicles').fetchall()
    drivers= conn.execute('SELECT * FROM Drivers').fetchall()
    conn.close()

    return render_template('index.html',vehicles=vehicles, drivers=drivers)

@app.route('/add_trip', methods=['POST'])
def add_trip():
    vehicle_id = request.form['vehicle_id']
    driver_id=request.form['driver_id']
    date=request.form['date']
    distance = request.form['distance']
    cost = request.form['cost']

    conn=get_db_connection()

    try: #Check if a driver is free or booked
        existing_trip=conn.execute('SELECT * FROM Trips WHERE DriverID = ? AND Date = ?', (driver_id, date)).fetchone()

        if existing_trip:
            conn.rollback()
            conn.close()
            flash(f"Booking canceled! Driver is already booked the date: {date}.", "error")
            return redirect(url_for('index'))
        #If driver is free, add the trip
        conn.execute('INSERT INTO Trips (VehicleID, DriverID, Date, Distance, Cost) VALUES (?, ?, ?, ?, ?)', (vehicle_id, driver_id, date, distance, cost))

        conn.commit()
        flash("Trip booked successfully!", "succes")

    except sqlite3.Error as e:
        conn.rollback()
        return f"A database error occurred: {e}"
        
    finally:  
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)