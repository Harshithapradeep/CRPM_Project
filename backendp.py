import mysql.connector
import pandas as pd
from decimal import Decimal

# MySQL connection
class DatabaseManager:
    def __init__(self, host='localhost', database='customer_management', user='root', password='admin@123'):
        # Establish a connection to the MySQL database
        self.conn = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        if self.conn.is_connected():
            print("Successfully connected to the database")
        else:
            print("Failed to connect to the database")

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            self.conn.commit()  # Commit the changes to the database
            return cursor
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()  # Return all rows from the query result
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
        finally:
            cursor.close()


class CustomerManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_customer(self, name, email, phone):
        query = "INSERT INTO Customers (name, email, phone) VALUES (%s, %s, %s)"
        self.db_manager.execute_query(query, (name, email, phone))

    def get_customers(self):
        # Fetch only active customers (active = 1)
        query = "SELECT * FROM Customers WHERE active=1"
        return self.db_manager.fetch_all(query)

    def update_customer(self, customer_id, name, email, phone):
        query = "UPDATE Customers SET name = %s, email = %s, phone = %s WHERE id = %s"
        self.db_manager.execute_query(query, (name, email, phone, customer_id))

    def delete_customer(self, customer_id):
        # Mark the customer as inactive (soft delete)
        query = "UPDATE Customers SET active = 0 WHERE id = %s"
        self.db_manager.execute_query(query, (customer_id,))


class ProductManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_product(self, name, price, stock):
        query = "INSERT INTO Products (name, price, stock) VALUES (%s, %s, %s)"
        self.db_manager.execute_query(query, (name, price, stock))

    def get_products(self):
        # Fetch only active products (active = 1)
        query = "SELECT * FROM Products WHERE active=1"
        return self.db_manager.fetch_all(query)

    def update_product(self, product_id, name, price, stock):
        query = "UPDATE Products SET name = %s, price = %s, stock = %s WHERE id = %s"
        self.db_manager.execute_query(query, (name, price, stock, product_id))

    def delete_product(self, product_id):
        # Mark the product as inactive (soft delete)
        query = "UPDATE Products SET active = 0 WHERE id = %s"
        self.db_manager.execute_query(query, (product_id,))


class PurchaseManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def record_purchase(self, customer_id, product_id, quantity):
        # First, validate that the product exists and is active
        product = self.db_manager.fetch_all(
            "SELECT id, price, stock FROM Products WHERE id=%s AND active=1",  # Corrected SQL
            (product_id,)
        )
        if not product:
            raise ValueError("Invalid or inactive product ID.")
        
        # Ensure that the product has enough stock
        if product[0][2] < quantity:
            raise ValueError("Insufficient stock for the product.")
        
        price = product[0][1]
        total_cost = price * quantity
        
        # Insert the purchase record into the Purchases table
        self.db_manager.execute_query(
            "INSERT INTO Purchases (customer_id, product_id, quantity, total_cost) VALUES (%s, %s, %s, %s)",  # Corrected SQL
            (customer_id, product_id, quantity, total_cost)
        )
        
        # Update product stock in the Products table
        self.db_manager.execute_query(
            "UPDATE Products SET stock = stock - %s WHERE id=%s",  # Corrected SQL
            (quantity, product_id)
        )

    def get_purchase_history(self, customer_id):
        query = """
            SELECT Products.name, Purchases.quantity, Purchases.total_cost
            FROM Purchases
            JOIN Products ON Purchases.product_id = Products.id
            WHERE Purchases.customer_id = %s AND Products.active = 1  # Corrected SQL
            ORDER BY Purchases.total_cost DESC
        """
        return self.db_manager.fetch_all(query, (customer_id,))

# Analytics function 

def get_sales_report(db_manager):
    query = """
        SELECT 
            SUM(Purchases.total_cost) AS total_revenue, 
            COUNT(Purchases.id) AS total_sales,  -- Count  purchase IDs
            SUM(Purchases.quantity) AS total_products_sold,
            SUM(Products.stock) AS total_stock_remaining
        FROM Purchases
        JOIN Products ON Purchases.product_id = Products.id
        WHERE Products.active = 1  -- Only consider active products
    """
    
    # Fetch the result (this returns a list of tuples)
    result = db_manager.fetch_all(query)

    # Ensure we check if result is not empty
    if result:
        # Access values using tuple indices
        total_revenue = result[0][0]  # First value in the first tuple is total_revenue
        total_sales = int(result[0][1])  # Ensure total_sales is an integer (from COUNT)
        total_products_sold = result[0][2]  # Third value in the first tuple is total_products_sold
        total_stock_remaining = result[0][3]  # Fourth value in the first tuple is total_stock_remaining
        
        # If any value is a Decimal, convert it to an integer or float as needed
        if isinstance(total_revenue, Decimal):
            total_revenue = float(total_revenue)  # Convert to float for currency representation
        if isinstance(total_products_sold, Decimal):
            total_products_sold = int(total_products_sold)  # Convert to int for quantity
        if isinstance(total_stock_remaining, Decimal):
            total_stock_remaining = int(total_stock_remaining)  # Convert to int for stock

        # Return the values in a dictionary
        return {
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "total_products_sold": total_products_sold,
            "total_stock_remaining": total_stock_remaining
        }
    else:
        # Handle the case where no data is returned (empty result)
        return {
            "total_revenue": 0,
            "total_sales": 0,
            "total_products_sold": 0,
            "total_stock_remaining": 0
        }



def get_top_products(db_manager, limit=5):
    query = f"""
        SELECT Products.name, SUM(Purchases.quantity) AS total_sold, SUM(Products.stock) AS stock_left
        FROM Purchases
        JOIN Products ON Purchases.product_id = Products.id
        WHERE Products.active = 1  -- Only consider active products
        GROUP BY Products.id
        ORDER BY total_sold DESC
        LIMIT {limit}
    """
    result = db_manager.fetch_all(query)
    return [{"Product Name": product[0], "Total Sold": product[1], "Stock Left": product[2]} for product in result]

def get_least_products(db_manager, limit=2):
    query = f"""
        SELECT Products.name, SUM(Purchases.quantity) AS total_sold, SUM(Products.stock) AS stock_left
        FROM Purchases
        JOIN Products ON Purchases.product_id = Products.id
        WHERE Products.active = 1  -- Only consider active products
        GROUP BY Products.id
        ORDER BY total_sold ASC
        LIMIT {limit}
    """
    result = db_manager.fetch_all(query)
    return [{"Product Name": product[0], "Total Sold": product[1], "Stock Left": product[2]} for product in result]

def get_top_customers(db_manager, limit=5):
    query = f"""
        SELECT Customers.name, SUM(Purchases.total_cost) AS total_spent, COUNT(Purchases.id) AS total_purchases
        FROM Purchases
        JOIN Customers ON Purchases.customer_id = Customers.id
        WHERE Purchases.total_cost > 0
        GROUP BY Customers.id
        ORDER BY total_spent DESC
        LIMIT {limit}
    """
    result = db_manager.fetch_all(query)
    return [{"Customer Name": customer[0], "Total Spent": customer[1], "Total Purchases": customer[2]} for customer in result]


def visualize_product_performance(db_manager):
    # Query to visualize the product performance trends (best-selling and least-selling)
    top_products = get_top_products(db_manager)
    least_products = get_least_products(db_manager)
    
    performance_data = {
        "best_selling_products": top_products,
        "least_selling_products": least_products
    }
    return performance_data

















