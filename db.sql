CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT
);
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    reference VARCHAR
);
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    started_date TIMESTAMP,
    completed_date TIMESTAMP,
    description TEXT,
    label TEXT,
    -- custom user label, not in import data
    notes TEXT,
    amount REAL,
    fee REAL,
    currency VARCHAR,
    type VARCHAR CHECK(type IN ('incoming', 'outgoing')),
    account_id INTEGER,
    import_hash VARCHAR UNIQUE,
    category_id INTEGER,
    FOREIGN KEY (account_id) REFERENCES accounts (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
);
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS transaction_tag (
    transaction_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);