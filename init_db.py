import sqlite3

#Create and connect to the database file
connection = sqlite3.connect('fleet.db')

#Run schema.sql to build tables
with open('schema.sql') as f:
    connection.executescript(f.read())

#Create a cursor to add data
cur = connection.cursor()

#Add sample data
cur.execute("INSERT INTO Drivers (Name, LicenseType) VALUES (?, ?)", ('John Johansson', 'B'))
cur.execute("INSERT INTO Drivers (Name, LicenseType) VALUES (?, ?)", ('Anna Anderson', 'C'))
cur.execute("INSERT INTO Drivers (Name, LicenseType) VALUES (?, ?)", ('Jacob Karlsson', 'B'))
cur.execute("INSERT INTO Drivers (Name, LicenseType) VALUES (?, ?)", ('Erik Svensson', 'CE'))
cur.execute("INSERT INTO Drivers (Name, LicenseType) VALUES (?, ?)", ('Axel Lindgren', 'C'))

cur.execute("INSERT INTO Vehicles (LicensePlate, Mileage, Status) VALUES (?, ?, ?)", ('QWE-123', 1000, 'Active'))
cur.execute("INSERT INTO Vehicles (LicensePlate, Mileage, Status) VALUES (?, ?, ?)", ('RTY-456', 4400, 'Active'))
cur.execute("INSERT INTO Vehicles (LicensePlate, Mileage, Status) VALUES (?, ?, ?)", ('UIO-789', 12000, 'Maintenance'))
cur.execute("INSERT INTO Vehicles (LicensePlate, Mileage, Status) VALUES (?, ?, ?)", ('AMH-285', 700, 'Active'))
cur.execute("INSERT INTO Vehicles (LicensePlate, Mileage, Status) VALUES (?, ?, ?)", ('LMO-916', 35000, 'Active'))

connection.commit()
connection.close()

print("Database 'fleet.db' initialized successfully and filled with sample data.")