"""Load the 6 Instacart CSV files into one SQLite database: data/instacart.db

Run once:  python load_data.py
Running it again deletes the old database and builds a new one.
"""
import sqlite3
import time
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "instacart.db"

# table name -> CSV file name
TABLES = {
    "aisles": "aisles.csv",
    "departments": "departments.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_products_prior": "order_products__prior.csv",
    "order_products_train": "order_products__train.csv",
}

# Read big files in pieces, so we don't need 32 million rows in memory at once.
CHUNK_SIZE = 1_000_000


def load_table(conn, table, csv_file):
    start = time.time()
    rows = 0
    for chunk in pd.read_csv(DATA_DIR / csv_file, chunksize=CHUNK_SIZE):
        chunk.to_sql(table, conn, if_exists="append", index=False)
        rows += len(chunk)
    conn.commit()
    print(f"  {table:<22} {rows:>12,} rows  ({time.time() - start:.0f}s)")


def create_indexes(conn):
    
    conn.execute("CREATE INDEX idx_products_aisle ON products(aisle_id)")
    conn.execute("CREATE INDEX idx_products_product ON products(product_id)")
    conn.execute("CREATE INDEX idx_products_department ON products(department_id)")
    conn.execute("CREATE INDEX idx_orders_order ON orders(order_id)")
    conn.execute("CREATE INDEX idx_orders_user ON orders(user_id)")
    conn.execute("CREATE INDEX idx_order_products_prior_order ON order_products_prior(order_id)")
    conn.execute("CREATE INDEX idx_order_products_prior_product ON order_products_prior(product_id)")
    conn.execute("CREATE INDEX idx_order_products_train_order ON order_products_train(order_id)")
    conn.execute("CREATE INDEX idx_order_products_train_product ON order_products_train(product_id)")


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    print("Loading tables...")
    for table, csv_file in TABLES.items():
        load_table(conn, table, csv_file)

    print("Creating indexes...")
    start = time.time()
    create_indexes(conn)
    conn.commit()
    print(f"  done ({time.time() - start:.0f}s)")

    conn.close()
    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
