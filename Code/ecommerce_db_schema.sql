-- 1. Create the Customers Table
DROP TABLE IF EXISTS customers CASCADE;
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,       -- Unique identifier for the customer
    age INT,                           -- Customer's age
    gender VARCHAR(10),                -- Customer's gender (e.g., 'Male', 'Female', 'Other')
    location VARCHAR(255),             -- Customer's location (e.g., city, region)
    review_rating FLOAT,               -- Average review rating
    subscription_status VARCHAR(20),   -- Subscription status (e.g., 'Active', 'Inactive')
    frequency_of_purchases VARCHAR(20) -- Frequency of purchases in months or a numerical value
);

-- 2. Create the Products Table
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY,        -- Unique identifier for the product
    product_name VARCHAR(255),          -- Name of the product
    brand_name VARCHAR(255),            -- Brand name
    category TEXT,                      -- Category of the product (e.g., 'Electronics', 'Clothing') 
    selling_price decimal(10,2),          -- Price at which the product is sold with currency symbol
    quantity INT,                       -- Quantity in stock
    model_number VARCHAR(500),           -- Model number for the product
    shipping_weight DECIMAL(10, 2),     -- Weight for shipping
    product_url TEXT,           -- URL for the product page
    stock INT,                          -- Current stock level of the product
    dimensions TEXT,            -- Product dimensions (length x width x height)
    color TEXT,                  -- Color of the product
    size TEXT,                          -- Size of the product (from Size Quantity Variant)
    product_description TEXT            -- Detailed product description
);

-- 3. Create the Transactions Table with Foreign Key Constraints and Partitioning
DROP TABLE IF EXISTS transactions CASCADE;
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL, -- Auto-incrementing primary key
    customer_id INT,                   -- FK referencing customer_id in the 'customers' table
    product_id UUID,                   -- FK referencing product_id in the 'products' table
    purchase_date TIMESTAMP,           -- Date and time of the purchase (Partition Key)
    purchase_amount_usd DECIMAL(10, 2),-- Amount spent on the product (USD)
    payment_method VARCHAR(50),        -- Payment method (e.g., 'Credit Card', 'PayPal')
    shipping_type VARCHAR(50),         -- Shipping type (e.g., 'Standard', 'Express')
    promo_code_used VARCHAR(50),       -- Promo code used for the transaction
    discount_applied DECIMAL(5, 2),    -- Discount applied (e.g., 10 for 10% discount)
    PRIMARY KEY (transaction_id, customer_id, product_id, purchase_date), -- Composite primary key
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE ON UPDATE CASCADE
)

PARTITION BY RANGE (purchase_date);

-- Create Partitions for Transactions Table
CREATE TABLE IF NOT EXISTS transactions_2023_q1
    PARTITION OF transactions
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

CREATE TABLE IF NOT EXISTS transactions_2023_q2
    PARTITION OF transactions
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');

CREATE TABLE IF NOT EXISTS transactions_2023_q3
    PARTITION OF transactions
    FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');

CREATE TABLE IF NOT EXISTS transactions_2023_q4
    PARTITION OF transactions
    FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');

CREATE TABLE IF NOT EXISTS transactions_old_data
    PARTITION OF transactions
    DEFAULT;
	
-- 4. Create the Interactions Table with Foreign Key Constraints
DROP TABLE IF EXISTS interactions CASCADE;
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id SERIAL PRIMARY KEY,  -- Auto-incremented unique ID
    user_id INT,                       -- FK referencing customer_id in the 'customers' table
    product_id UUID,                   -- FK referencing product_id in the 'products' table
    interaction_type VARCHAR(50),       -- Type of interaction (e.g., 'View', 'Click', 'Add to Cart')
    timestamp TIMESTAMP,                -- Time of interaction
    FOREIGN KEY (user_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 5. Create the Discounts Table with Foreign Key Constraints
DROP TABLE IF EXISTS discounts CASCADE;
CREATE TABLE IF NOT EXISTS discounts (
    promo_code_used VARCHAR(50),            -- Promo code used
    discount_applied DECIMAL(5, 2),         -- Discount percentage applied (e.g., 10 for 10%)
    transaction_id INT,                      -- FK referencing transaction_id in 'transactions'
    customer_id INT,                         -- FK referencing customer_id in 'transactions'
    product_id UUID,                         -- FK referencing product_id in 'transactions'
    purchase_date TIMESTAMP,                 -- FK referencing purchase_date in 'transactions'
    PRIMARY KEY (transaction_id, promo_code_used),  -- Ensure uniqueness per transaction
    FOREIGN KEY (transaction_id, customer_id, product_id, purchase_date)
        REFERENCES transactions (transaction_id, customer_id, product_id, purchase_date)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
-- 6. Create the Product Categories Table
DROP TABLE IF EXISTS product_categories CASCADE;
CREATE TABLE IF NOT EXISTS product_categories (
    category_id UUID PRIMARY KEY,    -- Unique identifier for the category
    category_name TEXT               -- Name of the category (e.g., 'Electronics', 'Clothing')
);


-- 7. Create the Product Variants Table
DROP TABLE IF EXISTS product_variants CASCADE;
CREATE TABLE IF NOT EXISTS product_variants (
    product_id UUID,                 -- FK referencing product_id in the 'products' table
    size TEXT,                -- Size of the product
    color TEXT,               -- Color of the product
    stock_quantity INT,              -- Quantity available for this variant
    PRIMARY KEY (product_id, size, color),  -- Composite primary key (for each size-color combination)
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 8. Create Indexes to Optimize Performance

-- 8.1. Index on 'customer_id' and 'product_id' for faster lookups in transactions
DROP INDEX IF EXISTS idx_customer_product;
CREATE INDEX idx_customer_product ON transactions (customer_id, product_id);

-- 8.2. Index on 'product_id' and 'purchase_date' to speed up product performance analysis over time
DROP INDEX IF EXISTS idx_product_purchase_date;
CREATE INDEX idx_product_purchase_date ON transactions (product_id, purchase_date);

-- 8.3. Index on 'category' in products for efficient category-based queries
DROP INDEX IF EXISTS idx_category;
CREATE INDEX idx_category ON products (category);

-- 8.4. Index on 'age' and 'gender' in customers to optimize demographic-based queries
DROP INDEX IF EXISTS idx_customer_demographics;
CREATE INDEX idx_customer_demographics ON customers (age, gender);

-- 8.5. Index on 'interaction_type' in interactions table for faster interaction analysis
DROP INDEX IF EXISTS idx_interaction_type;
CREATE INDEX idx_interaction_type ON interactions (interaction_type);


-- 9. Create Materialized View for Top-selling Products
DROP MATERIALIZED VIEW IF EXISTS top_selling_products;
CREATE MATERIALIZED VIEW IF NOT EXISTS top_selling_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.brand_name,
    p.category,
    COUNT(t.transaction_id) AS total_sales,
    SUM(t.purchase_amount_usd) AS total_revenue
FROM 
    transactions t
JOIN 
    products p ON t.product_id = p.product_id
GROUP BY 
    p.product_id, p.product_name, p.brand_name, p.category
ORDER BY 
    total_sales DESC;


-- 10. Create Summary Table for Customer Sales Insights (Denormalization Example)
DROP MATERIALIZED VIEW IF EXISTS customer_sales_summary;
CREATE MATERIALIZED VIEW IF NOT EXISTS customer_sales_summary AS
SELECT 
    c.customer_id,
    c.age,
    c.gender,
    c.location,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(t.purchase_amount_usd) AS total_spent,
    AVG(c.review_rating) AS avg_review_rating
FROM 
    customers c
JOIN 
    transactions t ON c.customer_id = t.customer_id
GROUP BY 
    c.customer_id, c.age, c.gender, c.location;
