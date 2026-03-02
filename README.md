# E-Commerce Management System (Python + PostgreSQL)

## Overview
CLI-based e-commerce management application built in **Python** using **PostgreSQL**. Supports product browsing and admin updates, customer registration/profile lookup, order creation and item handling, and product reviews. Includes SQL schema, seed data, views, indexes, stored procedures/functions, and a trigger to keep order totals consistent.

---

## Tech Stack
- **Python** (CLI app)
- **PostgreSQL** (schema: `ecommerce`)
- Library: `psycopg2`

---

## Features
### Product Management
- Search active products by name (case-insensitive)
- Filter products by category
- Add products
- Update product fields
- Soft delete (deactivate) products
- Low-stock report (threshold-based)

### Customer Management
- Register customers
- View customer profile
- Update customer info
- View customer order summaries
- Soft delete support via `isActive`

### Order Processing
- Create orders (starts as `Pending`)
- Add items to orders (checks stock, updates inventory)
- Auto-recalculate `totalAmount`
- Update order status
- Cancel order (restores stock)

### Reviews
- Add reviews
- View reviews per product
- Average rating for product
- Verify review flag (admin action)

---

## Database Schema
Schema: `ecommerce`

Tables:
- `Categories(categoryID PK, categoryName, description, isActive)`
- `Products(productID PK, productName, categoryID FK, price, stockQuantity, description, brand, weight, isActive)`
- `Customers(customerID PK, firstName, lastName, email UNIQUE, phone, dateOfBirth, registrationDate, isActive)`
- `Orders(orderID PK, customerID FK, orderDate, totalAmount, orderStatus, shippingAddress, paymentMethod)`
- `OrderItems(orderID FK, productID FK, quantity, unitPrice, subtotal, PRIMARY KEY(orderID, productID))`
- `Reviews(reviewID PK, customerID FK, productID FK, rating CHECK 1..5, reviewText, reviewDate, isVerified)`

---

## SQL Additions (Views, Indexes, Functions, Procedures, Triggers)
### Views
- `HighValueCustomersView`: aggregates total order amount + order count per customer
- `LowStockProductsView`: lists products under stock threshold (default logic uses `< 50`)

### Indexes
- `idx_email` on `Customers(email)`
- `idx_customer_date` on `Orders(customerID, orderDate)`
- `idx_productid` on `Reviews(productID)`
- `idx_order_product` on `OrderItems(orderID, productID)`

### Stored Functions / Procedures
- `checkProductStock(productID, quantity) -> BOOLEAN`
- `getRestockAlerts(threshold) -> TABLE(productID, productName, stockQuantity)`
- `placeOrder(customerID, shippingAddress, paymentMethod)` (procedure)
- `calculateOrderTotal(orderID)` (procedure)

### Trigger
- `orderitem_recalc_total`: fires on `OrderItems` insert/update/delete to recalculate `Orders.totalAmount`

---

## Setup / Run Instructions
### 1) Create DB + Schema + Tables
Run the SQL file that:
- creates schema `ecommerce`
- creates all 6 tables

### 2) Seed Sample Data (optional)
Run the provided insert statements for:
- categories, products, customers, orders, order items, reviews

### 3) Create views / indexes / functions / procedures / trigger
Run the SQL section that defines:
- views
- indexes
- stored procedures/functions
- trigger function + trigger

### 4) Ensure correct schema search path
Your Python queries reference tables directly (e.g., `FROM Products`), so Postgres must resolve them in `ecommerce`.

Recommended (session-level):
```sql
SET search_path TO ecommerce, public;
