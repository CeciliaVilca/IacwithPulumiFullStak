CREATE TABLE IF NOT EXISTS clinc150 (
    id SERIAL PRIMARY KEY,
    text TEXT,
    clean_text TEXT,
    intent VARCHAR(255)
);
