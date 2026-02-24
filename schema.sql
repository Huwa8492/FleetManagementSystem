-- Deletes the tables if they already exists
DROP TABLE IF EXISTS Maintenance;
DROP TABLE IF EXISTS Trips;
DROP TABLE IF EXISTS Vehicles;
DROP TABLE IF EXISTS Drivers;

CREATE TABLE Drivers (
    DriverID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(50) NOT NULL,
    LicenseType VARCHAR(50) NOT NULL
);

CREATE TABLE Vehicles (
    VehicleID INTEGER PRIMARY KEY AUTOINCREMENT,
    LicensePlate VARCHAR(50) UNIQUE NOT NULL,
    Mileage INTEGER DEFAULT (0),
    Status VARCHAR(50) DEFAULT 'Active'
);

CREATE TABLE Maintenance (
    MaintenanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID INTEGER NOT NULL,
    Date DATE NOT NULL,
    Cost REAL,
    Description VARCHAR(255) NOT NULL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID)
);

CREATE TABLE Trips (
    TripID INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID INTEGER NOT NULL,
    DriverID INTEGER NOT NULL,
    Date DATE NOT NULL,
    Distance INTEGER NOT NULL,
    Cost REAL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID),
    FOREIGN KEY (DriverID) REFERENCES Drivers(DriverID)
);

CREATE TRIGGER Check_Maintenance_Trigger
AFTER INSERT ON Trips
BEGIN
    UPDATE Vehicles
    SET
    Mileage = Mileage + NEW.Distance,
    Status = CASE
                WHEN (Mileage + NEW.Distance) >= 10000 THEN 'Maintenance Required'
                ELSE Status
            END
    WHERE VehicleID = NEW.VehicleID;
END;