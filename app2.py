import streamlit as st
import pandas as pd
# from urllib.parse import quote
from backendp import DatabaseManager, CustomerManager, ProductManager, PurchaseManager, get_sales_report, get_top_products, get_least_products,get_top_customers,visualize_product_performance


# Initialize MySQL connection and managers
db_manager = DatabaseManager(host='localhost', database='customer_management', user='root', password='admin@123')
customer_manager = CustomerManager(db_manager)
product_manager = ProductManager(db_manager)
purchase_manager = PurchaseManager(db_manager)

# Streamlit Navigation
st.sidebar.title("CRPM System")
menu = st.sidebar.radio(
    "Navigation", ["Customer Management", "Product Management", "Purchases", "Analytics"]
)

if menu == "Customer Management":
    st.title("Customer Management")
    choice = st.selectbox("Action", ["Add Customer", "View Customers", "Update Customer", "Delete Customer"])

    if choice == "Add Customer":
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        if st.button("Add"):
            customer_manager.add_customer(name, email, phone)
            st.success("Customer added successfully.")
    elif choice == "View Customers":
        customers = customer_manager.get_customers()
        df_customers = pd.DataFrame(customers, columns=["ID", "Name", "Email", "Phone", "Active"])
        st.write(df_customers)
    elif choice == "Update Customer":
        customer_id = st.number_input("Customer ID", min_value=1)
        name = st.text_input("New Name")
        email = st.text_input("New Email")
        phone = st.text_input("New Phone")
        if st.button("Update"):
            customer_manager.update_customer(customer_id, name, email, phone)
            st.success("Customer updated successfully.")
    elif choice == "Delete Customer":
        customer_id = st.number_input("Customer ID", min_value=1)
        if st.button("Delete"):
            customer_manager.delete_customer(customer_id)
            st.success("Customer deleted successfully.")
            # Refresh the customer list after deletion
            customers = customer_manager.get_customers()
            df_customers = pd.DataFrame(customers, columns=["ID", "Name", "Email", "Phone", "Active"])
            st.write(df_customers)

elif menu == "Product Management":
    st.title("Product Management")
    choice = st.selectbox("Action", ["Add Product", "View Products", "Update Product", "Delete Product"])

    if choice == "Add Product":
        name = st.text_input("Name")
        price = st.number_input("Price", min_value=0.0)
        stock = st.number_input("Stock", min_value=0)
        if st.button("Add"):
            product_manager.add_product(name, price, stock)
            st.success("Product added successfully.")
    elif choice == "View Products":
        products = product_manager.get_products()
        df_products = pd.DataFrame(products, columns=["ID", "Name", "Price", "Stock", "Active"])
        st.write(df_products)
    elif choice == "Update Product":
        product_id = st.number_input("Product ID", min_value=1)
        name = st.text_input("New Name")
        price = st.number_input("New Price", min_value=0.0)
        stock = st.number_input("New Stock", min_value=0)
        if st.button("Update"):
            product_manager.update_product(product_id, name, price, stock)
            st.success("Product updated successfully.")
    elif choice == "Delete Product":
        product_id = st.number_input("Product ID", min_value=1)
        if st.button("Delete"):
            product_manager.delete_product(product_id)
            st.success("Product deleted successfully.")
            # Refresh the product list after deletion
            products = product_manager.get_products()
            df_products = pd.DataFrame(products, columns=["ID", "Name", "Price", "Stock", "Active"])
            st.write(df_products)

elif menu == "Purchases":
    st.title("Purchases")

    # Input fields for customer and product details
    customer_id = st.number_input("Customer ID", min_value=1)
    product_id = st.number_input("Product ID", min_value=1)
    quantity = st.number_input("Quantity", min_value=1)

    # Add a selectbox for choosing actions
    choice = st.selectbox("Action", ["Select Action", "Record Purchase", "View Purchase History"])

    if choice == "Record Purchase":
        try:
            # Record the purchase
            purchase_manager.record_purchase(customer_id, product_id, quantity)
            st.success("Purchase recorded successfully.")

            # Fetch and display the updated purchase history
            st.header("Purchase History")
            purchases = purchase_manager.get_purchase_history(customer_id)

            if purchases:
                df_purchases = pd.DataFrame(purchases, columns=["Product Name", "Quantity", "Total Cost"])
                st.write(df_purchases)
            else:
                st.info("No purchase history available for this customer.")
        
        except ValueError as e:
            st.error(f"Error: {str(e)}")

    elif choice == "View Purchase History" and customer_id:
        # Only display the purchase history if the customer_id is provided
        st.header("Purchase History")
        purchases = purchase_manager.get_purchase_history(customer_id)
        
        if purchases:
            df_purchases = pd.DataFrame(purchases, columns=["Product Name", "Quantity", "Total Cost"])
            st.write(df_purchases)
        else:
            st.info("No purchase history available for this customer.")


elif menu == "Analytics":
    st.title("Analytics and Reports")

    # Sales Report
    st.header("Sales Report")
    sales_report = get_sales_report(db_manager)  # Fetch the updated sales report
    st.metric("Total Revenue", f"${sales_report['total_revenue']:.2f}")
    st.metric("Total Sales", sales_report['total_sales'])
    st.metric("Total Products Sold", sales_report['total_products_sold'])
    st.metric("Total Stock Remaining", sales_report['total_stock_remaining'])


    # Top Customers
    st.header("Top Customers")
    top_customers = get_top_customers(db_manager)
    df_top_customers = pd.DataFrame(top_customers, columns=["Customer Name", "Total Spent", "Total Purchases"])
    st.write(df_top_customers)

    # Product Performance Visualization (Best-Selling and Least-Selling)
    st.header("Product Performance Trends")
    performance_data = visualize_product_performance(db_manager)

    # Best-Selling Products
    st.subheader("Best-Selling Products")
    df_best_selling = pd.DataFrame(performance_data['best_selling_products'], columns=["Product Name", "Total Sold", "Stock Left"])
    st.write(df_best_selling)

    # Least-Selling Products
    st.subheader("Least-Selling Products")
    df_least_selling = pd.DataFrame(performance_data['least_selling_products'], columns=["Product Name", "Total Sold", "Stock Left"])
    st.write(df_least_selling)






















