PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Drivers (
    DriverID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(50) NOT NULL,
    LicenseType VARCHAR(50) NOT NULL
);
INSERT INTO Drivers VALUES(1,'John Johansson','B');
INSERT INTO Drivers VALUES(2,'Anna Anderson','C');
INSERT INTO Drivers VALUES(3,'Jacob Karlsson','B');
INSERT INTO Drivers VALUES(4,'Erik Svensson','CE');
INSERT INTO Drivers VALUES(5,'Axel Lindgren','C');
CREATE TABLE Vehicles (
    VehicleID INTEGER PRIMARY KEY AUTOINCREMENT,
    LicensePlate VARCHAR(50) UNIQUE NOT NULL,
    Mileage INTEGER DEFAULT (0),
    Status VARCHAR(50) DEFAULT 'Active'
);
INSERT INTO Vehicles VALUES(1,'QWE-123',70123,'Active');
INSERT INTO Vehicles VALUES(2,'RTY-456',4400,'Active');
INSERT INTO Vehicles VALUES(3,'UIO-789',12000,'Maintenance Required');
INSERT INTO Vehicles VALUES(4,'AMH-285',700,'Active');
INSERT INTO Vehicles VALUES(5,'LMO-916',35000,'Active');
CREATE TABLE Maintenance (
    MaintenanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID INTEGER NOT NULL,
    Date DATE NOT NULL,
    Cost REAL,
    Description VARCHAR(255) NOT NULL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID)
);
INSERT INTO Maintenance VALUES(1,2,'2026-03-13',20000.0,'Oil change');
INSERT INTO Maintenance VALUES(2,1,'2026-03-12',10000.0,'Service');
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
INSERT INTO Trips VALUES(1,1,2,'2026-03-11',123,2000.0);
INSERT INTO Trips VALUES(2,1,2,'2026-03-06',1000,20000.0);
INSERT INTO Trips VALUES(3,1,1,'2026-05-23',5000,15000.0);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('Drivers',5);
INSERT INTO sqlite_sequence VALUES('Vehicles',5);
INSERT INTO sqlite_sequence VALUES('Trips',3);
INSERT INTO sqlite_sequence VALUES('Maintenance',2);
CREATE TRIGGER Check_Maintenance_Trigger
AFTER INSERT ON Trips
BEGIN
    UPDATE Vehicles
    SET
        Status = CASE
                WHEN (Mileage + NEW.Distance)/10000 > Mileage/10000 THEN 'Maintenance Required'
                ELSE Status
            END,
        Mileage = Mileage + NEW.Distance
    WHERE VehicleID = NEW.VehicleID;
END;
CREATE TRIGGER Prevent_Active_Vehicle_Deletion
BEFORE DELETE ON Vehicles
BEGIN 
    SELECT CASE
        WHEN OLD.Status = 'Active' THEN
            RAISE(ABORT, 'Cannot delete a vehicle that is currently active.')
    END;
END;
COMMIT;
