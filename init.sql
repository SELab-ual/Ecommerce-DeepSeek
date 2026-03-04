-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    role VARCHAR(50) DEFAULT 'customer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    isbn13 VARCHAR(13) UNIQUE,
    title VARCHAR(500) NOT NULL,
    subtitle VARCHAR(500),
    author VARCHAR(255),
    publisher VARCHAR(255),
    publication_date DATE,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    cover_image_url TEXT,
    description TEXT,
    product_type VARCHAR(50) DEFAULT 'book',
    page_count INTEGER,
    language VARCHAR(50),
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cart table
CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, session_id)
);

-- Cart items table
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID REFERENCES carts(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, product_id)
);

-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    subtotal DECIMAL(10, 2) NOT NULL,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    shipping_address JSONB,
    billing_address JSONB,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_title VARCHAR(500) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table for guest users
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    data JSONB,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_products_isbn13 ON products(isbn13);
CREATE INDEX idx_products_title ON products(title);
CREATE INDEX idx_products_author ON products(author);
CREATE INDEX idx_products_product_type ON products(product_type);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_session_id ON orders(session_id);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Insert sample data
INSERT INTO products (isbn13, title, author, publisher, publication_date, price, cover_image_url, description, product_type, stock_quantity) VALUES
('9783161484100', 'The Pragmatic Programmer', 'David Thomas', 'Addison-Wesley', '2019-07-30', 49.99, '/assets/images/placeholder-cover.jpg', 'Your journey to mastery. 20th Anniversary Edition', 'book', 50),
('9780132350884', 'Clean Code', 'Robert C. Martin', 'Prentice Hall', '2008-08-01', 47.99, '/assets/images/placeholder-cover.jpg', 'A Handbook of Agile Software Craftsmanship', 'book', 35),
('9781491950296', 'Designing Data-Intensive Applications', 'Martin Kleppmann', 'O''Reilly Media', '2017-04-18', 54.99, '/assets/images/placeholder-cover.jpg', 'The Big Ideas Behind Reliable, Scalable, and Maintainable Systems', 'book', 25),
('9781617298691', 'Grooking Algorithms', 'Aditya Bhargava', 'Manning', '2016-05-25', 44.99, '/assets/images/placeholder-cover.jpg', 'An illustrated guide for programmers and other curious people', 'book', 40),
('9781492052203', 'Database Internals', 'Alex Petrov', 'O''Reilly Media', '2019-10-15', 59.99, '/assets/images/placeholder-cover.jpg', 'A Deep Dive into How Distributed Data Systems Work', 'book', 15);
