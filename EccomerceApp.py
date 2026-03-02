import psycopg2  # For PostgreSQL (or use mysql.connector for MySQL)
from psycopg2 import sql, Error
from datetime import datetime
from decimal import Decimal


class DatabaseConnection:
    """Handles database connection and operations"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Establish connection to your database.
        Update the credentials as per your environment.
        """
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="Ecommerce",  # replace with your DB name
                user="postgres",        # replace with your DB user
                password="password",  # replace with your DB password
                port="5432"
            )
            self.cursor = self.connection.cursor()
            print("Database connection successful!")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=None):
        """
        Execute a SELECT query and return results.  Any exceptions
        are caught and logged, and None is returned on failure.
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Query error: {e}")
            return None

    def execute_update(self, query, params=None):
        """
        Execute an INSERT/UPDATE/DELETE statement.  Commits the
        transaction on success, or rolls back on failure.
        Returns True on success, False on error.
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Update error: {e}")
            return False


class ProductManagement:
    """Handles all product-related operations"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def search_products(self, search_term: str):
        """
        Search active products whose names contain the provided search_term.
        The search is case-insensitive and uses SQL LIKE with wildcards.
        Returns a list of tuples representing the matching products or None on error.
        """
        query = """
            SELECT productID, productName, price, stockQuantity, brand
            FROM Products
            WHERE productName ILIKE %s AND isActive = TRUE
        """
        return self.db.execute_query(query, (f"%{search_term}%",))

    def filter_by_category(self, category_id: int):
        """
        Retrieve all active products in the specified category.  If the
        category_id does not exist, an empty list is returned.
        """
        query = """
            SELECT p.productID, p.productName, p.price, p.stockQuantity,
                   c.categoryName, p.brand
            FROM Products p
            JOIN Categories c ON p.categoryID = c.categoryID
            WHERE p.categoryID = %s AND p.isActive = TRUE
        """
        return self.db.execute_query(query, (category_id,))

    def get_low_stock_products(self, threshold: int = 50):
        """
        Return all active products with stockQuantity below the given threshold.
        Results are ordered by stockQuantity ascending so that the lowest
        stock products appear first.
        """
        query = """
            SELECT productID, productName, stockQuantity, brand
            FROM Products
            WHERE stockQuantity < %s AND isActive = TRUE
            ORDER BY stockQuantity ASC
        """
        return self.db.execute_query(query, (threshold,))

    def add_product(self, name: str, categoryID: int, price: Decimal,
                    stock: int, description: str, brand: str, weight: Decimal):
        """
        Insert a new product into the database.  Generates a new productID
        based on the current maximum productID and returns the new ID on
        success.  Uses execute_update to ensure the insert is committed.
        """
        # Generate next productID
        row = self.db.execute_query("SELECT COALESCE(MAX(productID), 100) + 1 FROM Products")
        productID = row[0][0] if row else 101

        insert_sql = """
            INSERT INTO Products
            (productID, productName, categoryID, price, stockQuantity, description, brand, weight, isActive)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """
        params = (productID, name, categoryID, price, stock, description, brand, weight)
        if self.db.execute_update(insert_sql, params):
            return productID
        return None

    def update_product(self, product_id: int, **kwargs):
        """
        Update one or more fields of an existing product identified by product_id.
        Only fields provided via kwargs will be updated.  Allowed keys include
        productName, categoryID, price, stockQuantity, description, brand, weight,
        and isActive.  Returns True if the update succeeded, False otherwise.
        """
        if not kwargs:
            print("No update parameters provided.")
            return False

        set_clauses = []
        values = []
        for field, value in kwargs.items():
            set_clauses.append(f"{field} = %s")
            values.append(value)
        # Append the product_id for the WHERE clause
        values.append(product_id)
        set_statement = ", ".join(set_clauses)
        query = f"UPDATE Products SET {set_statement} WHERE productID = %s"
        return self.db.execute_update(query, tuple(values))

    def deactivate_product(self, product_id: int):
        """
        Soft-delete a product by setting its isActive flag to FALSE.  Returns
        True if the update succeeded, False otherwise.
        """
        query = "UPDATE Products SET isActive = FALSE WHERE productID = %s"
        return self.db.execute_update(query, (product_id,))


class CustomerManagement:
    """Handles customer-related operations"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def register_customer(self, first_name: str, last_name: str, email: str,
                          phone: str, dob: str):
        """
        Register a new customer.  The registrationDate is set to the current
        date automatically.  Returns the new customerID on success.  If
        the email already exists (violates UNIQUE constraint), None is returned.
        """
        query = """
            INSERT INTO Customers
            (firstName, lastName, email, phone, dateOfBirth, registrationDate, isActive)
            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, TRUE)
            RETURNING customerID
        """
        try:
            self.db.cursor.execute(query, (first_name, last_name, email, phone, dob))
            new_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            return new_id
        except Exception as e:
            # On constraint violation or other error, roll back
            self.db.connection.rollback()
            print(f"Error registering customer: {e}")
            return None

    def get_customer_profile(self, customer_id: int):
        """
        Retrieve a customer's profile by ID.  Returns a single record or
        None if the customer does not exist.
        """
        query = """
            SELECT customerID, firstName, lastName, email, phone, dateOfBirth,
                   registrationDate, isActive
            FROM Customers
            WHERE customerID = %s
        """
        results = self.db.execute_query(query, (customer_id,))
        return results[0] if results else None

    def update_customer_info(self, customer_id: int, **kwargs):
        """
        Update a customer's contact details.  Accepts keyword arguments for
        phone, email, and other editable fields.  Returns True if the update
        succeeded.
        """
        if not kwargs:
            print("No update parameters provided.")
            return False
        set_clauses = []
        values = []
        for field, value in kwargs.items():
            set_clauses.append(f"{field} = %s")
            values.append(value)
        values.append(customer_id)
        set_statement = ", ".join(set_clauses)
        query = f"UPDATE Customers SET {set_statement} WHERE customerID = %s"
        return self.db.execute_update(query, tuple(values))

    def get_customer_orders(self, customer_id: int):
        """
        Retrieve summaries of all orders placed by a specific customer.
        Each row includes the orderID, orderDate, totalAmount, orderStatus,
        and the number of items in the order.
        """
        query = """
            SELECT o.orderID, o.orderDate, o.totalAmount, o.orderStatus,
                   COUNT(oi.productID) as item_count
            FROM Orders o
            LEFT JOIN OrderItems oi ON o.orderID = oi.orderID
            WHERE o.customerID = %s
            GROUP BY o.orderID
            ORDER BY o.orderDate DESC
        """
        return self.db.execute_query(query, (customer_id,))


class OrderManagement:
    """Handles order processing and management"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create_order(self, customer_id: int, shipping_address: str, payment_method: str):
        """
        Create a new order with an initial totalAmount of 0 and status 'Pending'.
        Returns the newly created orderID on success.
        """
        query = """
            INSERT INTO Orders
            (customerID, orderDate, totalAmount, orderStatus, shippingAddress, paymentMethod)
            VALUES (%s, CURRENT_DATE, 0, 'Pending', %s, %s)
            RETURNING orderID
        """
        try:
            self.db.cursor.execute(query, (customer_id, shipping_address, payment_method))
            order_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            return order_id
        except Exception as e:
            self.db.connection.rollback()
            print(f"Error creating order: {e}")
            return None

    def add_order_item(self, order_id: int, product_id: int, quantity: int):
        """
        Add an item to an existing order.  Checks stock availability, inserts the
        order item, updates product stock, and recalculates the order total.
        Returns True on success, False otherwise.
        """
        # Check stock availability and retrieve price
        check_query = """
            SELECT stockQuantity, price
            FROM Products
            WHERE productID = %s AND isActive = TRUE
        """
        product_info = self.db.execute_query(check_query, (product_id,))
        if not product_info:
            print("Product not found or inactive.")
            return False
        stock, price = product_info[0]
        if quantity > stock:
            print(f"Insufficient stock. Only {stock} units available.")
            return False
        # Calculate subtotal
        subtotal = Decimal(price) * Decimal(quantity)
        insert_query = """
            INSERT INTO OrderItems (orderID, productID, quantity, unitPrice, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """
        update_stock = """
            UPDATE Products
            SET stockQuantity = stockQuantity - %s
            WHERE productID = %s
        """
        try:
            # Begin transaction implicitly; execute both statements and commit
            self.db.cursor.execute(insert_query, (order_id, product_id, quantity, price, subtotal))
            self.db.cursor.execute(update_stock, (quantity, product_id))
            self.db.connection.commit()
            # Recalculate order total after adding the item
            self.calculate_order_total(order_id)
            return True
        except Exception as e:
            self.db.connection.rollback()
            print(f"Error adding item to order: {e}")
            return False

    def calculate_order_total(self, order_id: int):
        """
        Calculate and update the totalAmount for the given orderID by summing
        the subtotals of all associated OrderItems.  Returns True on success.
        """
        query = """
            UPDATE Orders
            SET totalAmount = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM OrderItems
                WHERE orderID = %s
            )
            WHERE orderID = %s
        """
        return self.db.execute_update(query, (order_id, order_id))

    def update_order_status(self, order_id: int, new_status: str):
        """
        Update the status of an order.  Allowed statuses include 'Pending',
        'Shipped', 'Delivered', and 'Cancelled'.  Returns True if the update
        succeeded.
        """
        query = "UPDATE Orders SET orderStatus = %s WHERE orderID = %s"
        return self.db.execute_update(query, (new_status, order_id))

    def cancel_order(self, order_id: int):
        """
        Cancel an order by restoring its items' quantities back to stock and
        setting the orderStatus to 'Cancelled'.  Returns True on success,
        False if the order has no items or an error occurs.
        """
        items_query = "SELECT productID, quantity FROM OrderItems WHERE orderID = %s"
        items = self.db.execute_query(items_query, (order_id,))
        if not items:
            print("Order not found or has no items to cancel.")
            return False
        try:
            for product_id, quantity in items:
                restore_query = """
                    UPDATE Products
                    SET stockQuantity = stockQuantity + %s
                    WHERE productID = %s
                """
                self.db.cursor.execute(restore_query, (quantity, product_id))
            status_query = "UPDATE Orders SET orderStatus = 'Cancelled' WHERE orderID = %s"
            self.db.cursor.execute(status_query, (order_id,))
            self.db.connection.commit()
            return True
        except Exception as e:
            self.db.connection.rollback()
            print(f"Error cancelling order: {e}")
            return False

    def get_order_details(self, order_id: int):
        """
        Get complete details for an order, including customer info and all
        associated items.  Returns a list of tuples or None if the order
        does not exist.
        """
        query = """
            SELECT o.orderID, o.orderDate, o.totalAmount, o.orderStatus, o.shippingAddress, o.paymentMethod,
                   c.customerID, c.firstName, c.lastName,
                   p.productID, p.productName, oi.quantity, oi.unitPrice, oi.subtotal
            FROM Orders o
            JOIN Customers c ON o.customerID = c.customerID
            LEFT JOIN OrderItems oi ON o.orderID = oi.orderID
            LEFT JOIN Products p ON oi.productID = p.productID
            WHERE o.orderID = %s
            ORDER BY oi.productID
        """
        return self.db.execute_query(query, (order_id,))


class ReviewManagement:
    """Handles product reviews"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def add_review(self, customer_id: int, product_id: int, rating: int, review_text: str):
        """
        Add a product review.  Optionally verify that the customer has purchased
        the product before allowing the review.  Returns the new reviewID on
        success.
        """
        # Optional: verify purchase
        verify_query = """
            SELECT COUNT(*) FROM OrderItems oi
            JOIN Orders o ON oi.orderID = o.orderID
            WHERE o.customerID = %s AND oi.productID = %s
        """
        try:
            self.db.cursor.execute(verify_query, (customer_id, product_id))
            count = self.db.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error verifying purchase: {e}")
            return None
        # Insert review regardless of purchase; could add logic to enforce
        insert_query = """
            INSERT INTO Reviews
            (customerID, productID, rating, reviewText, reviewDate, isVerified)
            VALUES (%s, %s, %s, %s, CURRENT_DATE, FALSE)
            RETURNING reviewID
        """
        try:
            self.db.cursor.execute(insert_query, (customer_id, product_id, rating, review_text))
            review_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            return review_id
        except Exception as e:
            self.db.connection.rollback()
            print(f"Error adding review: {e}")
            return None

    def get_product_reviews(self, product_id: int):
        """
        Retrieve all reviews for a product along with the reviewer's name.
        Reviews are ordered by reviewDate descending.
        """
        query = """
            SELECT r.reviewID, r.rating, r.reviewText, r.reviewDate, r.isVerified,
                   c.firstName, c.lastName
            FROM Reviews r
            JOIN Customers c ON r.customerID = c.customerID
            WHERE r.productID = %s
            ORDER BY r.reviewDate DESC
        """
        return self.db.execute_query(query, (product_id,))

    def get_average_rating(self, product_id: int):
        """
        Calculate and return the average rating and review count for a product.
        Returns a tuple (avg_rating, review_count) or (None, 0) if there are no reviews.
        """
        query = """
            SELECT AVG(rating) as avg_rating, COUNT(*) as review_count
            FROM Reviews
            WHERE productID = %s
        """
        result = self.db.execute_query(query, (product_id,))
        return result[0] if result else (None, 0)

    def verify_review(self, review_id: int):
        """
        Mark a review as verified.  Returns True on success.
        """
        query = "UPDATE Reviews SET isVerified = TRUE WHERE reviewID = %s"
        return self.db.execute_update(query, (review_id,))


class StoredProcedures:
    """
    Wrapper methods to call stored procedures and functions defined in the database.
    These procedures must exist in your PostgreSQL database for the calls to succeed.
    """

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def call_place_order(self, customer_id: int, shipping_address: str, payment_method: str):
        """
        Call the placeOrder stored procedure.  Returns any result returned by the
        stored procedure or None if no result is returned.
        """
        query = "CALL placeOrder(%s, %s, %s)"
        try:
            self.db.cursor.execute(query, (customer_id, shipping_address, payment_method))
            result = None
            try:
                result = self.db.cursor.fetchone()
            except Exception:
                pass  # procedure may not return a row
            self.db.connection.commit()
            return result
        except Exception as e:
            self.db.connection.rollback()
            print(f"Error calling placeOrder procedure: {e}")
            return None

    def call_check_stock(self, product_id: int, quantity: int):
        """
        Call the checkProductStock function to determine if sufficient stock
        exists for the requested quantity.  Returns True or False.
        """
        query = "SELECT checkProductStock(%s, %s)"
        try:
            result = self.db.execute_query(query, (product_id, quantity))
            return result[0][0] if result else None
        except Exception as e:
            print(f"Error calling checkProductStock: {e}")
            return None

    def call_restock_alert(self, threshold: int = 50):
        """
        Call the getRestockAlerts function to retrieve products below the given
        stock threshold.  Returns a list of tuples.
        """
        query = "SELECT * FROM getRestockAlerts(%s)"
        try:
            return self.db.execute_query(query, (threshold,))
        except Exception as e:
            print(f"Error calling getRestockAlerts: {e}")
            return None


class ECommerceApp:
    """Main application class with CLI interface"""

    def __init__(self):
        self.db = DatabaseConnection()
        if self.db.connect():
            self.products = ProductManagement(self.db)
            self.customers = CustomerManagement(self.db)
            self.orders = OrderManagement(self.db)
            self.reviews = ReviewManagement(self.db)
            self.procedures = StoredProcedures(self.db)
        else:
            print("Failed to connect to database. Exiting.")
            exit(1)

    def display_menu(self):
        """Display main menu options"""
        print("E-COMMERCE MANAGEMENT SYSTEM")
        print("1. Product Management")
        print("2. Customer Management")
        print("3. Order Processing")
        print("4. Review Management")
        print("5. Reports & Analytics")
        print("0. Exit")
        print()

    def product_menu(self):
        """
        Handle product management operations: search, filter, add, update,
        and view low stock items.  Loops until the user chooses to return
        to the main menu.
        """
        while True:
            print("\n--- Product Management ---")
            print("1. Search Products")
            print("2. Filter by Category")
            print("3. Add New Product")
            print("4. Update Product")
            print("5. View Low Stock Items")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            if choice == "1":
                term = input("Enter product name to search: ").strip()
                results = self.products.search_products(term)
                if results:
                    print("\nSearch Results:")
                    for row in results:
                        print(f"ID: {row[0]}, Name: {row[1]}, Price: ${row[2]:.2f}, Stock: {row[3]}, Brand: {row[4]}")
                else:
                    print("No products found.")
            elif choice == "2":
                cat_id = input("Enter category ID to filter by: ").strip()
                if not cat_id.isdigit():
                    print("Invalid category ID.")
                    continue
                results = self.products.filter_by_category(int(cat_id))
                if results:
                    print("\nProducts in Category:")
                    for row in results:
                        print(f"ID: {row[0]}, Name: {row[1]}, Price: ${row[2]:.2f}, Stock: {row[3]}, Category: {row[4]}, Brand: {row[5]}")
                else:
                    print("No products found for this category.")
            elif choice == "3":
                try:
                    name = input("Product name: ").strip()
                    cat_id = int(input("Category ID: ").strip())
                    price = Decimal(input("Price: ").strip())
                    stock = int(input("Stock quantity: ").strip())
                    description = input("Description: ").strip()
                    brand = input("Brand: ").strip()
                    weight = Decimal(input("Weight (kg): ").strip())
                except Exception as e:
                    print(f"Invalid input: {e}")
                    continue
                new_id = self.products.add_product(name, cat_id, price, stock, description, brand, weight)
                if new_id:
                    print(f"Product added with ID {new_id}.")
                else:
                    print("Failed to add product.")
            elif choice == "4":
                pid = input("Enter product ID to update: ").strip()
                if not pid.isdigit():
                    print("Invalid product ID.")
                    continue
                updates = {}
                print("Leave a field blank to keep current value.")
                new_price = input("New price: ").strip()
                if new_price:
                    try:
                        updates['price'] = Decimal(new_price)
                    except Exception:
                        print("Invalid price value.")
                        continue
                new_stock = input("New stock quantity: ").strip()
                if new_stock:
                    if new_stock.isdigit():
                        updates['stockQuantity'] = int(new_stock)
                    else:
                        print("Invalid stock quantity.")
                        continue
                new_desc = input("New description: ").strip()
                if new_desc:
                    updates['description'] = new_desc
                new_brand = input("New brand: ").strip()
                if new_brand:
                    updates['brand'] = new_brand
                new_weight = input("New weight (kg): ").strip()
                if new_weight:
                    try:
                        updates['weight'] = Decimal(new_weight)
                    except Exception:
                        print("Invalid weight value.")
                        continue
                if updates:
                    success = self.products.update_product(int(pid), **updates)
                    print("Product updated." if success else "Failed to update product.")
                else:
                    print("No updates provided.")
            elif choice == "5":
                threshold_input = input("Enter stock threshold (default 50): ").strip()
                threshold = int(threshold_input) if threshold_input.isdigit() else 50
                results = self.products.get_low_stock_products(threshold)
                if results:
                    print("\nLow Stock Products:")
                    for row in results:
                        print(f"ID: {row[0]}, Name: {row[1]}, Stock: {row[2]}, Brand: {row[3]}")
                else:
                    print("No low stock products.")
            elif choice == "0":
                break
            else:
                print("Invalid option. Please try again.")

    def customer_menu(self):
        """
        Handle customer management operations: register, view profile,
        update information, and view customer orders.  Loops until
        the user chooses to return to the main menu.
        """
        while True:
            print("\n--- Customer Management ---")
            print("1. Register New Customer")
            print("2. View Customer Profile")
            print("3. Update Customer Information")
            print("4. View Customer Orders")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            if choice == "1":
                first = input("First name: ").strip()
                last = input("Last name: ").strip()
                email = input("Email: ").strip()
                phone = input("Phone: ").strip()
                dob = input("Date of birth (YYYY-MM-DD): ").strip()
                new_id = self.customers.register_customer(first, last, email, phone, dob)
                if new_id:
                    print(f"Customer registered with ID {new_id}.")
                else:
                    print("Failed to register customer.")
            elif choice == "2":
                cid = input("Enter customer ID: ").strip()
                if not cid.isdigit():
                    print("Invalid customer ID.")
                    continue
                profile = self.customers.get_customer_profile(int(cid))
                if profile:
                    (cid_val, fname, lname, email, phone, dob, reg_date, active) = profile
                    print(f"Customer ID: {cid_val}")
                    print(f"Name: {fname} {lname}")
                    print(f"Email: {email}")
                    print(f"Phone: {phone}")
                    print(f"DOB: {dob}")
                    print(f"Registered: {reg_date}")
                    print(f"Active: {active}")
                else:
                    print("Customer not found.")
            elif choice == "3":
                cid = input("Enter customer ID to update: ").strip()
                if not cid.isdigit():
                    print("Invalid customer ID.")
                    continue
                updates = {}
                print("Leave field blank to skip.")
                new_phone = input("New phone: ").strip()
                if new_phone:
                    updates['phone'] = new_phone
                new_email = input("New email: ").strip()
                if new_email:
                    updates['email'] = new_email
                if updates:
                    success = self.customers.update_customer_info(int(cid), **updates)
                    print("Customer updated." if success else "Failed to update customer.")
                else:
                    print("No updates provided.")
            elif choice == "4":
                cid = input("Enter customer ID: ").strip()
                if not cid.isdigit():
                    print("Invalid customer ID.")
                    continue
                orders = self.customers.get_customer_orders(int(cid))
                if orders:
                    print("\nOrders:")
                    for row in orders:
                        print(f"Order ID: {row[0]}, Date: {row[1]}, Total: ${row[2]:.2f}, Status: {row[3]}, Items: {row[4]}")
                else:
                    print("No orders found for this customer.")
            elif choice == "0":
                break
            else:
                print("Invalid option. Please try again.")

    def order_menu(self):
        """
        Handle order processing operations: create, add item, update status,
        cancel, and view details.  Loops until the user chooses to return
        to the main menu.
        """
        while True:
            print("\n--- Order Processing ---")
            print("1. Create New Order")
            print("2. Add Item to Order")
            print("3. Update Order Status")
            print("4. Cancel Order")
            print("5. View Order Details")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            if choice == "1":
                cid = input("Customer ID: ").strip()
                if not cid.isdigit():
                    print("Invalid customer ID.")
                    continue
                address = input("Shipping address: ").strip()
                payment = input("Payment method: ").strip()
                order_id = self.orders.create_order(int(cid), address, payment)
                if order_id:
                    print(f"Order created with ID {order_id}.")
                else:
                    print("Failed to create order.")
            elif choice == "2":
                oid = input("Order ID: ").strip()
                pid = input("Product ID: ").strip()
                qty = input("Quantity: ").strip()
                if not (oid.isdigit() and pid.isdigit() and qty.isdigit()):
                    print("Invalid input. IDs and quantity must be numeric.")
                    continue
                success = self.orders.add_order_item(int(oid), int(pid), int(qty))
                print("Item added." if success else "Failed to add item.")
            elif choice == "3":
                oid = input("Order ID: ").strip()
                new_status = input("New status (Pending/Shipped/Delivered/Cancelled): ").strip()
                if not oid.isdigit():
                    print("Invalid order ID.")
                    continue
                success = self.orders.update_order_status(int(oid), new_status)
                print("Order status updated." if success else "Failed to update status.")
            elif choice == "4":
                oid = input("Order ID to cancel: ").strip()
                if not oid.isdigit():
                    print("Invalid order ID.")
                    continue
                success = self.orders.cancel_order(int(oid))
                print("Order cancelled." if success else "Failed to cancel order.")
            elif choice == "5":
                oid = input("Order ID: ").strip()
                if not oid.isdigit():
                    print("Invalid order ID.")
                    continue
                details = self.orders.get_order_details(int(oid))
                if details:
                    print("\nOrder Details:")
                    for row in details:
                        (order_id_val, order_date, total, status, address, payment_method,
                         customer_id, fname, lname,
                         product_id, product_name, qty, unit_price, subtotal) = row
                        print(f"Order ID: {order_id_val}, Date: {order_date}, Total: ${total:.2f}, Status: {status}")
                        print(f"Customer: {fname} {lname} (ID {customer_id})")
                        if product_id:
                            print(f"  - Product ID: {product_id}, Name: {product_name}, Qty: {qty}, Unit Price: ${unit_price:.2f}, Subtotal: ${subtotal:.2f}")
                    print()
                else:
                    print("Order not found or has no items.")
            elif choice == "0":
                break
            else:
                print("Invalid option. Please try again.")

    def review_menu(self):
        """
        Handle review management operations: add review, view product reviews,
        get average rating, and verify review.  Loops until the user
        chooses to return to the main menu.
        """
        while True:
            print("\n--- Review Management ---")
            print("1. Add Review")
            print("2. View Product Reviews")
            print("3. Get Average Rating")
            print("4. Verify Review (Admin)")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            if choice == "1":
                cid = input("Customer ID: ").strip()
                pid = input("Product ID: ").strip()
                rating = input("Rating (1-5): ").strip()
                review_text = input("Review text: ").strip()
                if not (cid.isdigit() and pid.isdigit() and rating.isdigit()):
                    print("Invalid input.")
                    continue
                rating_val = int(rating)
                if rating_val < 1 or rating_val > 5:
                    print("Rating must be between 1 and 5.")
                    continue
                review_id = self.reviews.add_review(int(cid), int(pid), rating_val, review_text)
                if review_id:
                    print(f"Review added with ID {review_id}.")
                else:
                    print("Failed to add review.")
            elif choice == "2":
                pid = input("Enter product ID: ").strip()
                if not pid.isdigit():
                    print("Invalid product ID.")
                    continue
                reviews = self.reviews.get_product_reviews(int(pid))
                if reviews:
                    print("\nProduct Reviews:")
                    for row in reviews:
                        (rid, rating_val, text, date, verified, fname, lname) = row
                        status = "Verified" if verified else "Unverified"
                        print(f"ID: {rid}, Rating: {rating_val}, Reviewer: {fname} {lname}, Date: {date}, Status: {status}")
                        print(f"  Review: {text}")
                else:
                    print("No reviews for this product.")
            elif choice == "3":
                pid = input("Enter product ID: ").strip()
                if not pid.isdigit():
                    print("Invalid product ID.")
                    continue
                avg, count = self.reviews.get_average_rating(int(pid))
                if count > 0 and avg is not None:
                    print(f"Average Rating: {float(avg):.2f} based on {count} review(s).")
                else:
                    print("No reviews to calculate average.")
            elif choice == "4":
                rid = input("Enter review ID to verify: ").strip()
                if not rid.isdigit():
                    print("Invalid review ID.")
                    continue
                success = self.reviews.verify_review(int(rid))
                print("Review verified." if success else "Failed to verify review.")
            elif choice == "0":
                break
            else:
                print("Invalid option. Please try again.")

    def run(self):
        """
        Main application loop.  Continuously display the main menu and
        delegate to the appropriate submenu based on user choice until
        the user chooses to exit.
        """
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip()
            if choice == "1":
                self.product_menu()
            elif choice == "2":
                self.customer_menu()
            elif choice == "3":
                self.order_menu()
            elif choice == "4":
                self.review_menu()
            elif choice == "0":
                print("Thank you for using E-Commerce System!")
                self.db.disconnect()
                break
            else:
                print("Invalid choice. Please try again.")


def main():
    """
    Entry point of the application.  Initializes and runs the ECommerceApp.
    """
    print("Starting E-Commerce Application...")
    app = ECommerceApp()
    app.run()


if __name__ == "__main__":
    main()