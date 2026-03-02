

-- Brett Knox
--assignment 3 (cop 3703 fall 2025)

-- schema
CREATE SCHEMA ecommerce;
SET search_path TO ecommerce;

-- 1) categories
CREATE TABLE Categories (
  categoryID    INT PRIMARY KEY,
  categoryName  VARCHAR(100) ,
  description   TEXT,
  isActive      BOOLEAN
);

-- 2) products
CREATE TABLE Products (
  productID      INT PRIMARY KEY,
  productName    VARCHAR(200) ,
  categoryID     INT REFERENCES Categories(categoryID),
  price          NUMERIC(10,2),
  stockQuantity  INT,
  description    TEXT,
  brand          VARCHAR(100),
  weight         NUMERIC(8,2),
  isActive       BOOLEAN
);

-- 3) customers
CREATE TABLE Customers (
  customerID       INT PRIMARY KEY,
  firstName        VARCHAR(100) ,
  lastName         VARCHAR(100) ,
  email            VARCHAR(150) UNIQUE,
  phone            VARCHAR(20),
  dateOfBirth      DATE,
  registrationDate DATE,
  isActive         BOOLEAN
);

-- 4) orders
CREATE TABLE Orders (
  orderID         INT PRIMARY KEY,
  customerID      INT REFERENCES Customers(customerID),
  orderDate       DATE,
  totalAmount     NUMERIC(12,2),
  orderStatus     VARCHAR(50),
  shippingAddress TEXT,
  paymentMethod   VARCHAR(50)
);

-- 5) orderitems
CREATE TABLE OrderItems (
  orderID    INT REFERENCES Orders(orderID),
  productID  INT REFERENCES Products(productID),
  quantity   INT,
  unitPrice  NUMERIC(10,2) ,
  subtotal   NUMERIC(12,2) ,
  PRIMARY KEY (orderID, productID)
);

-- 6) reviews
CREATE TABLE Reviews (
  reviewID    INT PRIMARY KEY,
  customerID  INT REFERENCES Customers(customerID),
  productID   INT REFERENCES Products(productID),
  rating      INT  CHECK (rating BETWEEN 1 AND 5),
  reviewText  TEXT,
  reviewDate  DATE,
  isVerified  BOOLEAN
);

-- instering things into the tables
-- ==========================================================
-- Insert Categories
INSERT INTO Categories (categoryID, categoryName, description, isActive) 
VALUES
(1, 'Electronics', 'Electronic devices and gadgets', TRUE),
(2, 'Clothing', 'Apparel and fashion items', TRUE),
(3, 'Books', 'Books and educational materials', TRUE),
(4, 'Home & Garden', 'Home improvement and gardening supplies', TRUE),
(5, 'Sports', 'Sports equipment and accessories', TRUE);


-- Insert Products
INSERT INTO Products (productID, productName, categoryID, price,
stockQuantity, description, brand, weight, isActive) VALUES
(101, 'iPhone 15 Pro', 1, 999.99, 50, 'Latest Apple smartphone', 'Apple', 0.19,
TRUE),
(102, 'Samsung Galaxy S24', 1, 899.99, 30, 'Premium Android smartphone',
'Samsung', 0.17, TRUE),
(103, 'MacBook Air M2', 1, 1299.99, 25, 'Lightweight laptop with M2 chip', 'Apple',
1.24, TRUE),
(104, 'Nike Air Max', 2, 129.99, 100, 'Comfortable running shoes', 'Nike', 0.8,
TRUE),
(105, 'Levi''s 501 Jeans', 2, 89.99, 75, 'Classic straight fit jeans', 'Levi''s', 0.6, TRUE),
(106, 'The Great Gatsby', 3, 12.99, 200, 'Classic American novel', 'Scribner', 0.3,
TRUE),
(107, 'Python Programming', 3, 49.99, 80, 'Learn Python programming',
'TechBooks', 1.2, TRUE),
(108, 'Coffee Maker', 4, 79.99, 40, 'Automatic drip coffee maker', 'Breville', 3.5,
TRUE),
(109, 'Yoga Mat', 5, 29.99, 60, 'Non-slip exercise mat', 'FitLife', 1.0, TRUE),
(110, 'Tennis Racket', 5, 149.99, 35, 'Professional tennis racket', 'Wilson', 0.3,
TRUE);


-- Insert Customers
INSERT INTO Customers (customerID, firstName, lastName, email, phone,
dateOfBirth, registrationDate, isActive) VALUES
(1001, 'John', 'Smith', 'john.smith@email.com', '555-0101', '1985-03-15', '2023-01-
15', TRUE),
(1002, 'Emily', 'Johnson', 'emily.j@email.com', '555-0102', '1990-07-22', '2023-02-
20', TRUE),
(1003, 'Michael', 'Brown', 'mbrown@email.com', '555-0103', '1988-11-10', '2023-
03-10', TRUE),
(1004, 'Sarah', 'Davis', 'sarah.davis@email.com', '555-0104', '1992-05-30', '2023-04-
05', TRUE),
(1005, 'David', 'Wilson', 'dwilson@email.com', '555-0105', '1987-09-18', '2023-05-
12', TRUE),
(1006, 'Lisa', 'Martinez', 'lisa.m@email.com', '555-0106', '1991-12-03', '2023-06-08',
FALSE);

-- Insert Orders
INSERT INTO Orders (orderID, customerID, orderDate, totalAmount, orderStatus,
shippingAddress, paymentMethod) VALUES
(2001, 1001, '2024-01-15', 1129.98, 'Delivered', '123 Main St, City, State 12345',
'Credit Card'),
(2002, 1002, '2024-01-20', 219.98, 'Shipped', '456 Oak Ave, City, State 12346',
'PayPal'),
(2003, 1003, '2024-02-01', 999.99, 'Delivered', '789 Pine St, City, State 12347',
'Credit Card'),
(2004, 1001, '2024-02-15', 89.99, 'Processing', '123 Main St, City, State 12345',
'Debit Card'),
(2005, 1004, '2024-03-01', 1379.98, 'Shipped', '321 Elm St, City, State 12348',
'Credit Card'),
(2006, 1002, '2024-03-10', 62.98, 'Delivered', '456 Oak Ave, City, State 12346',
'PayPal'),
(2007, 1005, '2024-03-15', 179.98, 'Pending', '654 Maple Dr, City, State 12349',
'Credit Card');


-- Insert OrderItems
INSERT INTO OrderItems (orderID, productID, quantity, unitPrice, subtotal)
VALUES
(2001, 101, 1, 999.99, 999.99),
(2001, 104, 1, 129.99, 129.99),
(2002, 104, 1, 129.99, 129.99),
(2002, 105, 1, 89.99, 89.99),
(2003, 101, 1, 999.99, 999.99),
(2004, 105, 1, 89.99, 89.99),
(2005, 103, 1, 1299.99, 1299.99),
(2005, 108, 1, 79.99, 79.99),
(2006, 106, 3, 12.99, 38.97),
(2006, 109, 1, 29.99, 29.99),
(2007, 110, 1, 149.99, 149.99),
(2007, 109, 1, 29.99, 29.99);

-- Insert Reviews
INSERT INTO Reviews (reviewID, customerID, productID, rating, reviewText,
reviewDate, isVerified) VALUES
(3001, 1001, 101, 5, 'Excellent phone! Battery life is amazing.', '2024-01-25',
TRUE),
(3002, 1002, 104, 4, 'Very comfortable shoes, great for running.', '2024-01-30',
TRUE),
(3003, 1003, 101, 5, 'Love the camera quality!', '2024-02-10', TRUE),
(3004, 1001, 104, 5, 'Perfect fit and very durable.', '2024-02-05', TRUE),
(3005, 1004, 103, 5, 'Fast performance and great design.', '2024-03-15', TRUE),
(3006, 1002, 106, 4, 'Classic book, good condition.', '2024-03-20', TRUE),
(3007, 1005, 110, 3, 'Good racket but a bit heavy for my preference.', '2024-03-25',
FALSE);


CREATE VIEW HighValueCustomersView AS
SELECT 
  c.customerID,
  c.firstName,
  c.lastName,
  c.email,
  SUM(o.totalAmount) AS totalOrderAmount,
  COUNT(o.orderID) AS orderCount
FROM Customers c
JOIN Orders o ON c.customerID = o.customerID
GROUP BY c.customerID, c.firstName, c.lastName, c.email;


SELECT * FROM HighValueCustomersView
WHERE totalOrderAmount > 500;



CREATE VIEW LowStockProductsView AS
SELECT 
  p.productID,
  p.productName,
  c.categoryName,
  p.stockQuantity,
  p.price
FROM Products p
JOIN Categories c ON p.categoryID = c.categoryID
WHERE p.stockQuantity < 50;


SELECT * FROM LowStockProductsView
WHERE categoryName = 'Electronics';


CREATE INDEX idx_email ON Customers(email);
CREATE INDEX idx_customer_date ON Orders(customerID, orderDate);
CREATE INDEX idx_productid ON Reviews(productID);
SELECT * FROM Reviews WHERE productID = 5;

CREATE INDEX idx_order_product ON OrderItems(orderID, productID);

SET search_path TO ecommerce;

CREATE OR REPLACE FUNCTION checkProductStock(p_productID INT, p_quantity INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS '
DECLARE
    available INT;
BEGIN
    SELECT stockQuantity INTO available
    FROM Products
    WHERE productID = p_productID AND isActive = TRUE;
    IF available IS NULL THEN
        RETURN FALSE;
    END IF;
    IF available >= p_quantity THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
';

CREATE OR REPLACE PROCEDURE placeOrder(
    p_customerID INT,
    p_shippingAddress TEXT,
    p_paymentMethod VARCHAR)
LANGUAGE plpgsql
AS '
DECLARE
    newOrderID INT;
BEGIN
    INSERT INTO Orders (customerID, orderDate, totalAmount, orderStatus, shippingAddress, paymentMethod)
    VALUES (p_customerID, CURRENT_DATE, 0, ''Pending'', p_shippingAddress, p_paymentMethod)
    RETURNING orderID INTO newOrderID;
    RAISE NOTICE ''Order created with ID %'', newOrderID;
END;
';

CREATE OR REPLACE PROCEDURE calculateOrderTotal(p_orderID INT)
LANGUAGE plpgsql
AS '
DECLARE
    newTotal NUMERIC(12,2);
BEGIN
    SELECT COALESCE(SUM(subtotal), 0)
    INTO newTotal
    FROM OrderItems
    WHERE orderID = p_orderID;
    UPDATE Orders
    SET totalAmount = newTotal
    WHERE orderID = p_orderID;
END;
';

CREATE OR REPLACE FUNCTION getRestockAlerts(p_threshold INT)
RETURNS TABLE(
    productID INT,
    productName VARCHAR,
    stockQuantity INT)
LANGUAGE plpgsql
AS '
BEGIN
    RETURN QUERY
    SELECT productID, productName, stockQuantity
    FROM Products
    WHERE stockQuantity < p_threshold
      AND isActive = TRUE
    ORDER BY stockQuantity ASC;
END;
';

CREATE OR REPLACE FUNCTION trg_update_order_total()
RETURNS TRIGGER
LANGUAGE plpgsql
AS '
BEGIN
    UPDATE Orders
    SET totalAmount = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM OrderItems
        WHERE orderID = NEW.orderID
    )
    WHERE orderID = NEW.orderID;
    RETURN NEW;
END;
';

CREATE TRIGGER orderitem_recalc_total
AFTER INSERT OR UPDATE OR DELETE
ON OrderItems
FOR EACH ROW
EXECUTE FUNCTION trg_update_order_total();

ALTER DATABASE Ecommerce SET search_path = zcommerce, public;
ALTER TABLE Customers
  ALTER COLUMN customerID
    ADD GENERATED ALWAYS AS IDENTITY;-- so it generates unique id's for every thing i insert 

ALTER TABLE Orders
  ALTER COLUMN orderID
    ADD GENERATED ALWAYS AS IDENTITY;
	
	ALTER TABLE Reviews
  ALTER COLUMN reviewID
    ADD GENERATED ALWAYS AS IDENTITY;
