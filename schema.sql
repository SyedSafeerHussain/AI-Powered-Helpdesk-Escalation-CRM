CREATE TABLE tickets(
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(255),
    subject VARCHAR(255),
    message TEXT,
    status VARCHAR(20) DEFAULT 'PENDING'
);