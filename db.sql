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
DROP VIEW IF EXISTS transactions_view;
CREATE VIEW transactions_view AS
SELECT transactions.*,
    TO_CHAR(started_date, 'YYYY-MM-DD HH24:MI:SS') as started,
    TO_CHAR(completed_date, 'YYYY-MM-DD HH24:MI:SS') as completed,
    accounts.name as account
FROM transactions
    JOIN accounts ON transactions.account_id = accounts.id
ORDER BY started_date ASC;
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS transactions_tags (
    transaction_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);