import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="budget.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, telegram_id INTEGER UNIQUE, 
            name TEXT, currency TEXT DEFAULT 'UZS', budget_limit INTEGER DEFAULT 0)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY, name TEXT, emoji TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY, user_id INTEGER, category_id INTEGER, 
            amount INTEGER, description TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        categories = [
            ('Ovqat', '🍔'), ('Transport', '🚌'), ('Uy', '🏠'), 
            ('Sog\'liq', '💊'), ('Ko\'ngil ochar', '🎮'), ('Ta\'lim', '📚'), 
            ('Kiyim', '👗'), ('Boshqa', '📦')
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO categories (name, emoji) VALUES (?, ?)", categories)
        self.conn.commit()

    def add_user(self, tg_id, name):
        self.cursor.execute("INSERT OR IGNORE INTO users (telegram_id, name) VALUES (?, ?)", (tg_id, name))
        self.conn.commit()

    def get_user(self, tg_id):
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (tg_id,))
        return self.cursor.fetchone()

    def update_budget(self, tg_id, limit):
        self.cursor.execute("UPDATE users SET budget_limit = ? WHERE telegram_id = ?", (limit, tg_id))
        self.conn.commit()

    def update_currency(self, tg_id, currency):
        self.cursor.execute("UPDATE users SET currency = ? WHERE telegram_id = ?", (currency, tg_id))
        self.conn.commit()

    def add_expense(self, tg_id, cat_name, amount, desc=""):
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
        cat_id = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO expenses (user_id, category_id, amount, description) VALUES (?, ?, ?, ?)",
                            (tg_id, cat_id, amount, desc))
        self.conn.commit()

    def get_monthly_total(self, tg_id):
        month = datetime.now().strftime('%m')
        self.cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ? AND strftime('%m', created_at) = ?", (tg_id, month))
        res = self.cursor.fetchone()[0]
        return res if res else 0

    def get_monthly_report(self, tg_id):
        month = datetime.now().strftime('%m')
        self.cursor.execute('''SELECT c.name, c.emoji, SUM(e.amount) 
                               FROM expenses e JOIN categories c ON e.category_id = c.id 
                               WHERE e.user_id = ? AND strftime('%m', e.created_at) = ?
                               GROUP BY c.name''', (tg_id, month))
        return self.cursor.fetchall()

db = Database()