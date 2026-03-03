from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

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

    try: 
        #Check that the date is not in the past
        trip_date=datetime.strptime(date, '%Y-%m-%d'). date()
        today = datetime.today().date()
        if trip_date < today:
            conn.close()
            flash("Booking canceled! You can not book a trip in the past.", "error")
            return redirect(url_for('index'))

        vehicle=conn.execute('SELECT Status FROM Vehicles WHERE VehicleID = ?', (vehicle_id,)).fetchone()

        if vehicle and vehicle['Status'] == 'Maintenance Required':
            conn.rollback()
            conn.close()
            flash("Booking cancelled! The chosen vehicle needs maintenance, please choose another.", "error")
            return redirect(url_for('index'))
        #Check if the vehicle is free
        existing_vehicle_trip = conn.execute('SELECT * FROM Trips WHERE VehicleID =? AND Date =?', (vehicle_id, date)).fetchone()

        if existing_vehicle_trip:
            conn.rollback()
            conn.close()
            flash(f"Booking canceled! The vehicle is already booked the date: {date}.", "error")
            return redirect(url_for('index'))
        
        maintenance_booking = conn.execute('SELECT * FROM Maintenance WHERE VehicleID = ? AND Date = ?', (vehicle_id, date)).fetchone()

        if maintenance_booking:
            conn.rollback()
            conn.close()
            flash(f"Booking canceled! The vehicle is in the workshop for maintenance on {date}.", "error")
            return redirect(url_for('index'))
        
        #Check if a driver is free or booked
        existing_trip=conn.execute('SELECT * FROM Trips WHERE DriverID = ? AND Date = ?', (driver_id, date)).fetchone()

        if existing_trip:
            conn.rollback()
            conn.close()
            flash(f"Booking canceled! Driver is already booked the date: {date}.", "error")
            return redirect(url_for('index'))
        #If driver is free, add the trip
        conn.execute('INSERT INTO Trips (VehicleID, DriverID, Date, Distance, Cost) VALUES (?, ?, ?, ?, ?)', (vehicle_id, driver_id, date, distance, cost))

        conn.commit()
        flash("Trip booked successfully!", "success")

    except sqlite3.Error as e:
        conn.rollback()
        return f"A database error occurred: {e}"
        
    finally:  
        conn.close()

    return redirect(url_for('index'))

@app.route('/add_maintenance', methods=['POST'])
def add_maintenance():
    vehicle_id=request.form['vehicle_id']
    date = request.form['date']
    cost = request.form['cost']
    description = request.form['description']

    conn=get_db_connection()

    try:
        existing_trip=conn.execute('SELECT * FROM Trips WHERE VehicleID =? AND Date = ?', (vehicle_id, date)).fetchone()

        if existing_trip:
            conn.rollback()
            conn.close()
            flash(f"Maintenance canceled! The vehicle is already booked for a trip on the date: {date}.", "error")
            return redirect(url_for('index'))

        conn.execute('INSERT INTO Maintenance (VehicleID, Date, Cost, Description) VALUES (?, ?, ?, ?)', (vehicle_id, date, cost, description))
        
        conn.execute("UPDATE Vehicles SET Status = 'Active' WHERE VehicleID=?", (vehicle_id,))

        conn.commit()
        flash("Maintenance logged successfully! The vehicle is now active and ready to drive", "success")

    except sqlite3.Error as e:
        conn.rollback()
        flash(f"A database error occurred: {e}", "error")

    finally:
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)