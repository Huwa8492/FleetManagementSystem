from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key='secret_key_for_flash'

#Connect to the database
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='GODIS-gris04',
        database='FleetManagement'
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM Vehicles')
    vehicles=cursor.fetchall()
    cursor.execute('SELECT * FROM Drivers')
    drivers=cursor.fetchall()

    #Multirelation JOIN
    cursor.execute('''
    SELECT Trips.Date, Vehicles.LicensePlate, Drivers.Name, Trips.Distance, Trips.Cost, CALCULATE_TAX(Trips.Cost) as Tax 
    FROM Trips
    JOIN Vehicles ON Trips.VehicleID = Vehicles.VehicleID
    JOIN Drivers ON Trips.DriverID = Drivers.DriverID
    ORDER BY Trips.Date DESC''')
    trips_history = cursor.fetchall()

    #Aggregation and grouping
    cursor.execute('''
    SELECT Vehicles.LicensePlate, Vehicles.Status, Vehicles.Mileage, 
           COUNT(Trips.TripID) as TotalTrips, 
           SUM(Trips.Distance) as TotalDistance 
    FROM Vehicles 
    LEFT JOIN Trips ON Vehicles.VehicleID = Trips.VehicleID 
    GROUP BY Vehicles.VehicleID''')
    vehicle_stats = cursor.fetchall()

    cursor.execute('''
    SELECT Maintenance.Date, Vehicles.LicensePlate, Maintenance.Cost, Maintenance.Description 
    FROM Maintenance
    JOIN Vehicles ON Maintenance.VehicleID = Vehicles.VehicleID 
    ORDER BY Maintenance.Date DESC''')
    maintenance_history = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('index.html',vehicles=vehicles, drivers=drivers, trips_history=trips_history, vehicle_stats=vehicle_stats, maintenance_history=maintenance_history)

@app.route('/add_trip', methods=['POST'])
def add_trip():
    vehicle_id = request.form['vehicle_id']
    driver_id=request.form['driver_id']
    date=request.form['date']
    distance = request.form['distance']
    cost = request.form['cost']

    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)

    try: 
        #Check that the date is not in the past
        trip_date=datetime.strptime(date, '%Y-%m-%d'). date()
        today = datetime.today().date()
        if trip_date < today:
            flash("Booking canceled! You can not book a trip in the past.", "error")
            return redirect(url_for('index'))

        cursor.execute('SELECT Status FROM Vehicles WHERE VehicleID = %s', (vehicle_id,))
        vehicle = cursor.fetchone()

        if vehicle and vehicle['Status'] == 'Maintenance Required':
            flash("Booking cancelled! The chosen vehicle needs maintenance, please choose another.", "error")
            return redirect(url_for('index'))
            
        # Check if the vehicle is free
        cursor.execute('SELECT * FROM Trips WHERE VehicleID = %s AND Date = %s', (vehicle_id, date))
        existing_vehicle_trip = cursor.fetchone()

        if existing_vehicle_trip:
            flash(f"Booking canceled! The vehicle is already booked the date: {date}.", "error")
            return redirect(url_for('index'))
        
        cursor.execute('SELECT * FROM Maintenance WHERE VehicleID = %s AND Date = %s', (vehicle_id, date))
        maintenance_booking = cursor.fetchone()

        if maintenance_booking:
            flash(f"Booking canceled! The vehicle is in the workshop for maintenance on {date}.", "error")
            return redirect(url_for('index'))
        
        # Check if a driver is free or booked
        cursor.execute('SELECT * FROM Trips WHERE DriverID = %s AND Date = %s', (driver_id, date))
        existing_trip = cursor.fetchone()

        if existing_trip:
            flash(f"Booking canceled! Driver is already booked the date: {date}.", "error")
            return redirect(url_for('index'))
            
        # If driver is free, add the trip
        cursor.execute('INSERT INTO Trips (VehicleID, DriverID, Date, Distance, Cost) VALUES (%s, %s, %s, %s, %s)', (vehicle_id, driver_id, date, distance, cost))

        conn.commit()
        flash("Trip booked successfully!", "success")

    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"A database error occurred: {e}", "error")
        
    finally:  
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/add_maintenance', methods=['POST'])
def add_maintenance():
    vehicle_id=request.form['vehicle_id']
    date = request.form['date']
    cost = request.form['cost']
    description = request.form['description']

    conn=get_db_connection()
    cursor=conn.cursor()

    try:
        maintenance_date = datetime.strptime(date, '%Y-%m-%d').date()
        today = datetime.today().date()
        if maintenance_date < today:
            flash("Maintenance canceled! You cannot book maintenance in the past.", "error")
            return redirect(url_for('index'))
        
        cursor.execute('SELECT * FROM Trips WHERE VehicleID = %s AND Date = %s', (vehicle_id, date))
        existing_trip = cursor.fetchone()

        if existing_trip:
            flash(f"Maintenance canceled! The vehicle is already booked for a trip on the date: {date}.", "error")
            return redirect(url_for('index'))

        cursor.execute('INSERT INTO Maintenance (VehicleID, Date, Cost, Description) VALUES (%s, %s, %s, %s)', (vehicle_id, date, cost, description))
        cursor.execute("UPDATE Vehicles SET Status = 'Active' WHERE VehicleID=%s", (vehicle_id,))

        conn.commit()
        flash("Maintenance logged successfully! The vehicle is now active and ready to drive", "success")

    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"A database error occurred: {e}", "error")

    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)