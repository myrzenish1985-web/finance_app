import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('finance.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                balance REAL DEFAULT 0,
                created_date TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                account_id INTEGER,
                planned REAL DEFAULT 0,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                amount REAL,
                date TEXT,
                note TEXT,
                FOREIGN KEY (category_id) REFERENCES expense_categories (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account INTEGER,
                to_account INTEGER,
                amount REAL,
                date TEXT,
                note TEXT,
                FOREIGN KEY (from_account) REFERENCES accounts (id),
                FOREIGN KEY (to_account) REFERENCES accounts (id)
            )
        ''')
        
        self.conn.commit()
    
    def add_account(self, name, type_account, balance=0):
        date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute(
            'INSERT INTO accounts (name, type, balance, created_date) VALUES (?, ?, ?, ?)',
            (name, type_account, balance, date)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_accounts(self):
        self.cursor.execute('SELECT * FROM accounts ORDER BY id')
        return self.cursor.fetchall()
    
    def update_balance(self, account_id, new_balance):
        self.cursor.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_balance, account_id))
        self.conn.commit()
    
    def delete_account(self, account_id):
        self.cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        self.conn.commit()
    
    def add_category(self, name, account_id, planned=0):
        self.cursor.execute(
            'INSERT INTO expense_categories (name, account_id, planned) VALUES (?, ?, ?)',
            (name, account_id, planned)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_categories(self, account_id=None):
        if account_id:
            self.cursor.execute('SELECT * FROM expense_categories WHERE account_id = ?', (account_id,))
        else:
            self.cursor.execute('SELECT * FROM expense_categories')
        return self.cursor.fetchall()
    
    def add_expense(self, category_id, amount, note=''):
        date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute(
            'INSERT INTO expenses (category_id, amount, date, note) VALUES (?, ?, ?, ?)',
            (category_id, amount, date, note)
        )
        self.conn.commit()
        
        self.cursor.execute('''
            UPDATE accounts SET balance = balance - ? 
            WHERE id = (SELECT account_id FROM expense_categories WHERE id = ?)
        ''', (amount, category_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def add_transfer(self, from_acc, to_acc, amount, note=''):
        date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute(
            'INSERT INTO transfers (from_account, to_account, amount, date, note) VALUES (?, ?, ?, ?, ?)',
            (from_acc, to_acc, amount, date, note)
        )
        self.conn.commit()
        
        self.cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (amount, from_acc))
        self.cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, to_acc))
        self.conn.commit()
    
    def get_total_balance(self):
        self.cursor.execute('SELECT SUM(balance) FROM accounts')
        return self.cursor.fetchone()[0] or 0
    
    def get_plan_vs_fact(self):
        self.cursor.execute('''
            SELECT ec.name, ec.planned, COALESCE(SUM(e.amount), 0) as actual,
                   ec.planned - COALESCE(SUM(e.amount), 0) as remainder
            FROM expense_categories ec
            LEFT JOIN expenses e ON ec.id = e.category_id
            GROUP BY ec.id
        ''')
        return self.cursor.fetchall()
    
    def get_expenses_by_period(self, year, month=None):
        if month:
            self.cursor.execute('''
                SELECT ec.name, SUM(e.amount) 
                FROM expenses e
                JOIN expense_categories ec ON e.category_id = ec.id
                WHERE strftime('%Y', e.date) = ? AND strftime('%m', e.date) = ?
                GROUP BY ec.name
            ''', (str(year), f'{month:02d}'))
        else:
            self.cursor.execute('''
                SELECT strftime('%Y-%m', e.date) as month, SUM(e.amount)
                FROM expenses e
                WHERE strftime('%Y', e.date) = ?
                GROUP BY month
            ''', (str(year),))
        return self.cursor.fetchall()
    
    def get_transfers(self):
        self.cursor.execute('''
            SELECT t.id, a1.name as from_name, a2.name as to_name, t.amount, t.date, t.note
            FROM transfers t
            JOIN accounts a1 ON t.from_account = a1.id
            JOIN accounts a2 ON t.to_account = a2.id
            ORDER BY t.date DESC
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()
