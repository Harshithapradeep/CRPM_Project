
-- create database
create database if not exists customer_management 


-- Create Customers Table
CREATE TABLE IF NOT EXISTS customer_management.Customers (
    id INT auto_increment PRIMARY key,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    active INT DEFAULT 1
);

-- Create Products Table
CREATE TABLE IF NOT EXISTS customer_management.Products (
    id INTEGER auto_increment PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    active INTEGER DEFAULT 1
);


-- Create Purchases Table
CREATE TABLE IF NOT EXISTS customer_management.Purchases (
    id INTEGER auto_increment PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_cost REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers (id),
    FOREIGN KEY (product_id) REFERENCES Products (id)
);

-- Insert Sample Data
INSERT INTO customer_management.Customers (name, email, phone) VALUES ('John Doe', 'john@example.com', '1234567890');
INSERT INTO customer_management.Customers (name, email, phone) VALUES ('Jane Smith', 'jane@example.com', '0987654321');

INSERT INTO customer_management.customers (name, email, phone, active) VALUES 
('Alice Johnson', 'alice.j@example.com', '1112223333', 1),
('Bob Brown', 'bob.brown@example.com', '4445556666', 0);


INSERT INTO customer_management.products (name, price, stock, active) VALUES
('Laptop', 1200.00, 10, 1),
('Smartphone', 800.00, 25, 1),
('Headphones', 150.00, 50, 1),
('Tablet', 300.00, 15, 1),
('Smartwatch', 200.00, 0, 0);

select * from customer_management.products p 


INSERT INTO customer_management.products(name, price, stock) VALUES ('Product A', 10.0, 100);
INSERT INTO customer_management.Products (name, price, stock) VALUES ('Product B', 20.0, 50);
INSERT INTO customer_management.Products (name, price, stock) VALUES ('Product C', 30.0, 75);


select * from customer_management.customers c 

select * from customer_management.products p 

select * from customer_management.purchases p 

-- Insert Purchases
INSERT INTO customer_management.Purchases (customer_id, product_id, quantity, total_cost) VALUES
(1, 1, 1, 1200.00),
(2, 2, 2, 1600.00),
(1, 3, 3, 450.00),
(3, 4, 1, 300.00);
