DROP DATABASE IF EXISTS FleetManagement;
CREATE DATABASE FleetManagement;
USE FleetManagement;

CREATE TABLE Drivers (
    DriverID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    LicenseType VARCHAR(50) NOT NULL
);

CREATE TABLE Vehicles (
    VehicleID INT AUTO_INCREMENT PRIMARY KEY,
    LicensePlate VARCHAR(50) UNIQUE NOT NULL,
    Mileage INT DEFAULT (0),
    Status VARCHAR(50) DEFAULT 'Active'
);

CREATE TABLE Maintenance (
    MaintenanceID INT AUTO_INCREMENT PRIMARY KEY,
    VehicleID INT NOT NULL,
    Date DATE NOT NULL,
    Cost REAL,
    Description VARCHAR(255) NOT NULL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID)
);

CREATE TABLE Trips (
    TripID INT AUTO_INCREMENT PRIMARY KEY,
    VehicleID INT NOT NULL,
    DriverID INT NOT NULL,
    Date DATE NOT NULL,
    Distance INT NOT NULL,
    Cost DECIMAL(10,2),
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID),
    FOREIGN KEY (DriverID) REFERENCES Drivers(DriverID)
);

DELIMITER //
CREATE FUNCTION CALCULATE_TAX (trip_cost DECIMAL(10,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    IF trip_cost IS NULL THEN RETURN 0.00;
    END IF;
    RETURN ROUND(trip_cost * 0.25, 2);
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER Check_Maintenance_Trigger
AFTER INSERT ON Trips
FOR EACH ROW
BEGIN
    UPDATE Vehicles
    SET
        Status = CASE
                WHEN (Mileage + NEW.Distance) DIV 10000 > Mileage DIV 10000 THEN 'Maintenance Required'
                ELSE Status
            END,
        Mileage = Mileage + NEW.Distance
    WHERE VehicleID = NEW.VehicleID;
END //


CREATE TRIGGER Prevent_Active_Vehicle_Deletion
BEFORE DELETE ON Vehicles
FOR EACH ROW
BEGIN 
    IF OLD.Status = 'Active' THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Cannot delete a vehicle that is currently active.';
    END IF;
END //

DELIMITER ;