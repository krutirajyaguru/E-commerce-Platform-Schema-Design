# E-commerce Platform Schema Design

# Project Overview

This project is an ETL pipeline designed to extract, transform, and load data from various CSV files into a PostgreSQL database for an e-commerce platform. It involves several data sources that contain information about customers, products, transactions, and interactions. The data is transformed using PySpark and written to PostgreSQL tables for future analysis and reporting.

The primary components of the project are:

    * ETL Process: The Python script (etl.py) handles the process of extracting data, transforming it, and loading it into the PostgreSQL database.
    * Database Schema: The SQL schema (schema.sql) defines the structure of the database, including the tables, foreign key relationships, and indexes.
    * Data Sources: CSV files containing customer, transaction, and product data.
    Project Files

    * Customer Details CSV (customer_details.csv) - Contains customer information, reviews, and purchasing details.
    * E-commerce Sales Data CSV (ecommerce_sales_data_2024.csv) - Contains data on user-product interactions, including timestamps and interaction types.
    * Product Details CSV (product_details.csv) - Contains detailed information about products including pricing, dimensions, categories, and variants.

# Data Understanding

The project integrates data from three key CSV files, each with its own structure and meaning:

1. Customer Details (customer_details.csv)

This file contains details about customers and their purchasing behaviors. Key columns:

    - Customer ID: Unique identifier for each customer.
    - Age: Age of the customer.
    - Gender: Gender of the customer (Male, Female, Other).
    - Item Purchased: The product the customer purchased.
    - Category: Category of the purchased product (e.g., Electronics, Clothing).
    - Purchase Amount (USD): Total purchase amount in USD.
    - Location: The customer's location (e.g., city, country).
    - Review Rating: The rating given by the customer for the purchased product.
    - Subscription Status: The customer's subscription status (Active or Inactive).
    - Shipping Type: The type of shipping used by the customer (e.g., Standard, Express).
    - Discount Applied: Any discount applied to the purchase.
    - Promo Code Used: Promo code applied by the customer.
    - Payment Method: Method used for payment (e.g., Credit Card, PayPal).
    - Frequency of Purchases: How often the customer makes purchases (e.g., monthly).

2. E-commerce Sales Data (ecommerce_sales_data_2024.csv)

This file contains user interactions with products. Key columns:

    - user id: The unique ID of the user interacting with the product.
    - product id: The unique ID of the product being interacted with.
    - Interaction type: Type of interaction (e.g., View, Add to Cart, Purchase).
    - Time stamp: The date and time when the interaction occurred.

3. Product Details (product_details.csv)

This file contains detailed information about products. Key columns:

    - Uniqe Id: Unique identifier for the product.
    - Product Name: Name of the product.
    - Brand Name: Brand of the product.
    - Category: Category of the product (e.g., Electronics, Clothing).
    - Selling Price: The price at which the product is sold.
    - Quantity: The quantity of the product available.
    - Model Number: The model number of the product.
    - Shipping Weight: The weight of the product for shipping purposes.
    - Dimensions: Dimensions of the product.
    - Color: Color of the product.
    - Size Quantity Variant: Size variant of the product (e.g., Small, Medium, Large).
    - Product Description: A detailed description of the product.

# Data Modeling

1. Entities and Relationships

   The data in this project revolves around several key entities:
   
     1. Customers
         - Unique customers identified by customer_id.
         - Relationships:
             - Transactions: A customer can make multiple transactions, but each transaction is tied to one customer.
             - Interactions: A customer can interact with many products over time.
  
     2. Products
         - Unique products identified by product_id.
         - Relationships:
             - Transactions: A product can be involved in many transactions, where customers purchase them.
             - Interactions: A product can have multiple interactions, including views, adds to cart, and purchases.
             - Product Variants: Each product can have variants, such as different sizes and colors.
     
     3. Transactions
         - Each transaction is linked to one customer and one product, with details about the transaction such as purchase_amount_usd, payment_method, and shipping_type.
     
     4. Product Categories
         - Each product belongs to one category, and categories can contain many products.
     
     5. Discounts
         - Discounts are tied to transactions, where promo codes and discount percentages can be applied.
     
     6. Product Variants
         - Each product can have multiple variants (size, color) and a corresponding stock quantity.

2. Normalization: Defining Tables

   Normalization is applied to reduce redundancy and ensure data integrity. The database schema is designed based on normalized structures. Here's an overview of the normalization:
   
       - First Normal Form (1NF): Ensures that all attributes in a table contain atomic values. For instance, the products table stores individual product details, with each column containing a single piece of information.
   
       - Second Normal Form (2NF): Ensures that each non-key attribute is fully functionally dependent on the primary key. The transactions table is normalized such that all non-key attributes (like purchase_amount_usd and shipping_type) depend on the composite primary key (transaction_id, customer_id, product_id).
   
       - Third Normal Form (3NF): Eliminates transitive dependencies. For example, customer information (age, gender) is stored in the customers table, while transaction-specific data is stored in the transactions table.

3. ER Diagram

   An Entity-Relationship (ER) Diagram is a visual representation of how entities (tables) in a database are related to each other. It shows the structure and the relationships between these entities.
   
       * Let's go through each relationship in your ER diagram:
   
           1. Customers (1) ↔ (M) Transactions
   
               - This means one customer can have many transactions.
               - In the customers table, each customer has a unique customer_id, and in the transactions table, each transaction has a customer_id that links it back to a customer.
               - This is a one-to-many relationship. One customer can make multiple transactions.
               
           2. Products (1) ↔ (M) Transactions
   
               - This means one product can be part of many transactions.
               - In the products table, each product has a unique product_id, and in the transactions table, each transaction includes a product_id.
               - This is another one-to-many relationship. One product can be bought in multiple transactions.
   
           3. Products (1) ↔ (M) Interactions
   
               - This means one product can have many interactions.
               - In the products table, each product has a unique product_id, and in the interactions table, each interaction is tied to a product_id.
               -  This is a one-to-many relationship. A product can have multiple interactions like views, clicks, etc.
   
           4. Products (1) ↔ (M) Product Variants
   
               - This means one product can have many variants (like different sizes, colors).
               - In the products table, each product has a unique product_id, and in the product_variants table, each variant includes a product_id.
               - This is also a one-to-many relationship. One product can have many variants.
   
           5. Product Categories (1) ↔ (M) Products
   
               - This means one product category can contain many products.
               - In the product_categories table, each category has a unique category_id, and in the products table, each product is assigned to a category_id.
               - This is a one-to-many relationship. One category can have multiple products.
   
           6. Transactions (1) ↔ (M) Discounts
   
               - This means one transaction can have many discounts applied.
               - In the transactions table, each transaction has a unique transaction_id, and in the discounts table, each discount is tied to a specific transaction_id.
               - This is a one-to-many relationship. One transaction can have multiple discounts (for example, multiple promo codes or discounts applied to one purchase).
   
       * Summary of Relationships:
           One-to-Many (1:M) Relationships:
           - Customers ↔ Transactions
           - Products ↔ Transactions
           - Products ↔ Interactions
           - Products ↔ Product Variants
           - Product Categories ↔ Products
           - Transactions ↔ Discounts
   
       * Visualizing It:
   
           The ER Diagram would look like this conceptually:
   
           Customers <-----> Transactions <-----> Discounts
               ^                 ^
               |                 |
               v                 v
               Products <-----> Interactions
               ^
               |
               v
           Product Variants <-----> Product Categories
   
           * In this diagram:
   
               - Arrows represent relationships between tables.
               - The 1 side (one entity) points to the M side (many entities), showing that one record in the first table can relate to multiple records in the second table.
   
   This ER Diagram helps you understand the structure of your database and how the data flows between different entities. It shows how Customers interact with Transactions, how Products have multiple Variants, and how Discounts are applied to Transactions, among other relationships.

# Database Architecture

1. Database Design
The database is designed to handle large volumes of data from customers, products, transactions, and interactions. The key points of the design are:

    - Tables: Tables are created for customers, products, transactions, interactions, discounts, product categories, and product variants.
    - Foreign Keys: Relationships are established between tables using foreign keys:
    - Transactions references both customers and products.
    - Discounts references transactions.
    - Product Variants references products.
    - Indexes: To optimize query performance, indexes are created on frequently queried columns such as customer_id, - product_id, and purchase_date.
    - Partitioning: The transactions table is partitioned by purchase_date to optimize performance for time-based queries.

2. ETL Python File (etl.py)
The ETL Python File uses PySpark for data extraction, transformation, and loading:

    - Extract: Data is extracted from CSV files using PySpark's read.csv function.
    - Transform: The data is transformed using PySpark functions such as select, cast, dropna, and regexp_extract to clean, enrich, and reshape the data according to the database schema.
    - Load: The transformed data is written to PostgreSQL using the write.jdbc method.
    Key Functions in the ETL Script:
    - load_csv: Loads CSV files into PySpark DataFrames.
    - transform_customers, transform_products, transform_transactions: Transforms data into the desired structure.
    - write_to_postgres: Writes the transformed data to the PostgreSQL database.

# How to Run the Project

Prerequisites
    - Python 3.x: Make sure Python 3 is installed on your system.
    - PySpark: Install PySpark using pip install pyspark.
    - PostgreSQL: Set up a PostgreSQL database to store the data.
    - JDBC Driver: Ensure the PostgreSQL JDBC driver is available (postgresql-42.5.1.jar).
    - CSV Files: Download or prepare the customer_details.csv, ecommerce_sales_data_2024.csv, and product_details.csv files.


# Conclusion

This project demonstrates the ETL process using PySpark for large-scale data processing and PostgreSQL for data storage. By integrating customer, transaction, and product data, the system enables comprehensive analytics for an e-commerce platform.

# License
This project is licensed under the MIT License.
