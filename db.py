import sqlite3
conn = sqlite3.connect("shield.db", check_same_thread=False)
conn.row_factory = sqlite3.Row


conn.executescript("""
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY,
    site_key TEXT UNIQUE,
    secret TEXT,
    domain TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    site_key TEXT,
    token TEXT UNIQUE,
    ip TEXT,
    score INTEGER,
    verdict TEXT,
    reasons TEXT,
    used INTEGER DEFAULT 0,
    created_at INTEGER
);
""")


conn.execute("""
INSERT OR IGNORE INTO sites (site_key, secret, domain)
VALUES ('pk_test123', 'sk_test456', 'localhost')
""")

conn.commit()