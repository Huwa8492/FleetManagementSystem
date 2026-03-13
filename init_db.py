import mysql.connector

#Create and connect to the database file
connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='GODIS-gris04',
        database='FleetManagement'
    )

cursor = connection.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE Trips")
cursor.execute("TRUNCATE TABLE Maintenance")
cursor.execute("TRUNCATE TABLE Vehicles")
cursor.execute("TRUNCATE TABLE Drivers")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Add sample data
drivers_data = [
    ('John Johansson', 'B'),
    ('Anna Anderson', 'C'),
    ('Jacob Karlsson', 'B'),
    ('Erik Svensson', 'CE'),
    ('Axel Lindgren', 'C')
]
cursor.executemany("INSERT INTO Drivers (Name, LicenseType) VALUES (%s, %s)", drivers_data)

vehicles_data = [
    ('QWE-123', 64000, 'Active'),
    ('RTY-456', 4400, 'Active'),
    ('UIO-789', 12000, 'Maintenance Required'),
    ('AMH-285', 700, 'Active'),
    ('LMO-916', 35000, 'Active')
]
cursor.executemany("INSERT INTO Vehicles (LicensePlate, Mileage, Status) VALUES (%s, %s, %s)", vehicles_data)

connection.commit()
cursor.close()
connection.close()

print("Database 'FleetManagement' initialized successfully and filled with sample data.")