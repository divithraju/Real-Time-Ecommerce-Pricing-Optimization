CREATE DATABASE IF NOT EXISTS Ecommerce_data;
USE Ecommerce_data;
CREATE TABLE IF NOT EXISTS product_sales (
    transaction_id INT PRIMARY KEY,
    product_id INT,
    customer_id INT,
    amount DOUBLE,
    region VARCHAR(50),
    payment_mode VARCHAR(50),
    last_updated DATETIME
);
