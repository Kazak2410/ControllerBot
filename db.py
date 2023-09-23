import sqlite3


class DataBase:
    def __init__(self, filename):
        self.connection = sqlite3.connect(f"{filename}.db")
        self.cursor = self.connection.cursor()


    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_number INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                shelf_life TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)


    def add_product(self, product_number, name, category, shelf_life):
        self.cursor.execute("""
            INSERT OR IGNORE INTO products (product_number, name, category, shelf_life) VALUES (?, ?, ?, ?)
        """, (product_number, name, category, shelf_life))
        self.connection.commit()


    def check_table(self):
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='products')")
        exists = self.cursor.fetchone()[0]
        return exists


    def get_categories(self):
        self.cursor.execute("""
            SELECT name FROM categories
        """)

        categories = self.cursor.fetchall()
        return categories


    def get_products(self):
        self.cursor.execute("SELECT product_number, name, shelf_life FROM products")

        products = self.cursor.fetchall()
        return products
