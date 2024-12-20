DROP TABLE IF EXISTS OrderDetails;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Customers;

CREATE TABLE Customers (
    CustomerID VARCHAR(10) PRIMARY KEY,
    CustomerName VARCHAR(100) NOT NULL,
    Segment VARCHAR(50),
    Country VARCHAR(50),
    City VARCHAR(50),
    State VARCHAR(50),
    PostalCode VARCHAR(10),
    Region VARCHAR(50)
);

CREATE TABLE Orders (
    OrderID VARCHAR(15) PRIMARY KEY,
    OrderDate DATE NOT NULL,
    ShipDate DATE,
    ShipMode VARCHAR(50),
    CustomerID VARCHAR(10) NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

CREATE TABLE Products (
    ProductID VARCHAR(20) PRIMARY KEY,
    ProductName VARCHAR(255) NOT NULL,
    Category VARCHAR(50),
    SubCategory VARCHAR(50)
);

CREATE TABLE OrderDetails (
    RowID INT PRIMARY KEY,
    OrderID VARCHAR(15) NOT NULL,
    ProductID VARCHAR(20) NOT NULL,
    Sales DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

INSERT INTO Customers (CustomerID, CustomerName, Segment, Country, City, State, PostalCode, Region)
VALUES 
('CG-12520', 'Claire Gute', 'Consumer', 'United States', 'Henderson', 'Kentucky', '42420', 'South'),
('DV-13045', 'Darrin Van Huff', 'Corporate', 'United States', 'Los Angeles', 'California', '90036', 'West');

INSERT INTO Orders (OrderID, OrderDate, ShipDate, ShipMode, CustomerID)
VALUES 
('CA-2017-152156', '2017-08-11', '2017-11-11', 'Second Class', 'CG-12520'),
('CA-2016-138688', '2016-06-12', '2016-06-16', 'Standard Class', 'DV-13045');

INSERT INTO Products (ProductID, ProductName, Category, SubCategory)
VALUES 
('FUR-BO-10001798', 'Bush Somerset Collection Bookcase', 'Furniture', 'Bookcases'),
('OFF-LA-10000240', 'Luxo Lamp', 'Office Supplies', 'Lamps');

INSERT INTO OrderDetails (RowID, OrderID, ProductID, Sales)
VALUES 
(1, 'CA-2017-152156', 'FUR-BO-10001798', 261.96),
(2, 'CA-2016-138688', 'OFF-LA-10000240', 10.99);
