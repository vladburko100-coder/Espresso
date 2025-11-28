import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6 import uic


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1200, 700)
        uic.loadUi('main.ui', self)
        self.init_database()
        self.setup_connections()
        self.load_coffee_data()

    def init_database(self):
        self.conn = sqlite3.connect('coffee.sqlite')
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coffee (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                roast_degree TEXT NOT NULL,
                ground_whole TEXT NOT NULL,
                taste_description TEXT,
                price REAL NOT NULL,
                volume REAL NOT NULL
            )
        ''')

        sample_data = [
            ('Эфиопия Иргачефф', 'Светлая', 'В зернах', 'Цветочные ноты, бергамот, цитрус', 1250.00, 250),
            ('Колумбия Супремо', 'Средняя', 'Молотый', 'Ореховый, карамельный, шоколадный', 890.00, 500),
            ('Бразилия Сантос', 'Темная', 'В зернах', 'Шоколадный, пряный, дымный', 950.00, 250),
            ('Кения АА', 'Средняя', 'В зернах', 'Ягодный, винный, томатный', 1350.00, 250),
            ('Гватемала Антигуа', 'Средняя', 'Молотый', 'Шоколадный, ореховый, ванильный', 820.00, 500)
        ]

        for data in sample_data:
            cursor.execute('''
                INSERT OR IGNORE INTO coffee 
                (name, roast_degree, ground_whole, taste_description, price, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data)

        self.conn.commit()

    def setup_connections(self):
        self.searchInput.textChanged.connect(self.filter_data)
        self.roastFilter.currentTextChanged.connect(self.filter_data)
        self.typeFilter.currentTextChanged.connect(self.filter_data)

        self.coffeeTable.setSortingEnabled(True)

    def load_coffee_data(self, query=None, params=None):
        self.coffeeTable.setSortingEnabled(False)

        if query is None:
            query = 'SELECT id, name, roast_degree, ground_whole, taste_description, price, volume FROM coffee ORDER BY name'
            params = []

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        coffee_data = cursor.fetchall()

        self.coffeeTable.setRowCount(0)

        for row_data in coffee_data:
            row_position = self.coffeeTable.rowCount()
            self.coffeeTable.insertRow(row_position)

            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))

                if col_idx in [0, 5, 6]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.coffeeTable.setItem(row_position, col_idx, item)

        self.coffeeTable.setSortingEnabled(True)

    def filter_data(self):
        search_text = self.searchInput.text().strip()
        roast_filter = self.roastFilter.currentText()
        type_filter = self.typeFilter.currentText()

        query = 'SELECT id, name, roast_degree, ground_whole, taste_description, price, volume FROM coffee WHERE 1=1'
        params = []

        if search_text:
            query += ' AND (name LIKE ? OR taste_description LIKE ?)'
            params.extend([f'%{search_text}%', f'%{search_text}%'])

        if roast_filter != "Все":
            query += ' AND roast_degree = ?'
            params.append(roast_filter)

        if type_filter != "Все":
            query += ' AND ground_whole = ?'
            params.append(type_filter)

        query += ' ORDER BY name'

        self.load_coffee_data(query, params)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())