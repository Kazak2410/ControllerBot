import sqlite3


class DataBase:
    def __init__(self, filename):
        self.connection = sqlite3.connect(f"{filename}.db")
        self.cursor = self.connection.cursor()


    def create_tables(self):
        """Creates main tables"""
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

        default_categories = [
            ("Сыр",),
            ("Молочный продукт",),
            ("Сырокоп",),
            ("Полукоп",),
            ("Сыровял",),
            ("Варенка",),
            ("Деликатес",),
            ("Заморозка",),
            ("Напиток",),
            ("Соус",),
            ("Прочее",)
        ]

        self.cursor.executemany("INSERT INTO categories (name) VALUES (?)", default_categories)
        self.connection.commit()


    def add_product(self, product_number, name, category, shelf_life):
        """Adds product to the db"""
        self.cursor.execute("""
            INSERT OR IGNORE INTO products (product_number, name, category, shelf_life) VALUES (?, ?, ?, ?)
        """, (product_number, name, category, shelf_life))
        self.connection.commit()


    def delete_product(self, product_number, shelf_life):
        """Deletes product from db"""
        self.cursor.execute("""
            DELETE FROM products WHERE product_number = ? AND shelf_life = ?
        """, (product_number, shelf_life))
        self.connection.commit()


    def check_table(self):
        """Tables verification"""
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='products')")
        exists = self.cursor.fetchone()[0]
        return exists


    def get_categories(self):
        """Returns categories from db"""
        self.cursor.execute("""
            SELECT name FROM categories
        """)

        categories = self.cursor.fetchall()
        return categories


    def get_products(self):
        """Returns product list from db"""
        self.cursor.execute("SELECT product_number, name, shelf_life FROM products")

        products = self.cursor.fetchall()
        return products
