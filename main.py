import sys
import sqlite3
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox, QPushButton
from PyQt6.QtCore import Qt
from main_des import MainDesign
from edit_des import EditDesign


class AddEditCoffeeForm(QDialog, EditDesign):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.setupUi(self)
        self.coffee_id = coffee_id

        self.db_path = parent.db_path if parent else self.get_db_path()

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if coffee_id:
            self.load_coffee_data()

    def get_db_path(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        data_dir = os.path.join(application_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'coffee.sqlite')

    def load_coffee_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM coffee WHERE id = ?', (self.coffee_id,))
            coffee = cursor.fetchone()
            conn.close()
            if coffee:
                self.nameEdit.setText(coffee[1])
                index = self.roastCombo.findText(coffee[2])
                if index >= 0:
                    self.roastCombo.setCurrentIndex(index)
                index = self.typeCombo.findText(coffee[3])
                if index >= 0:
                    self.typeCombo.setCurrentIndex(index)
                self.tasteEdit.setText(coffee[4])
                self.priceSpin.setValue(float(coffee[5]))
                self.volumeSpin.setValue(int(coffee[6]))
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def get_data(self):
        return {
            'name': self.nameEdit.text(),
            'roast_degree': self.roastCombo.currentText(),
            'ground_whole': self.typeCombo.currentText(),
            'taste_description': self.tasteEdit.text(),
            'price': self.priceSpin.value(),
            'volume': self.volumeSpin.value()
        }


class CoffeeApp(QMainWindow, MainDesign):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setGeometry(100, 100, 1200, 700)

        self.db_path = self.get_db_path()

        self.init_database()
        self.setup_connections()
        self.load_coffee_data()

    def get_db_path(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        data_dir = os.path.join(application_path, 'data')
        os.makedirs(data_dir, exist_ok=True)

        return os.path.join(data_dir, 'coffee.sqlite')

    def init_database(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
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
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось инициализировать базу данных: {str(e)}")

    def setup_connections(self):
        self.searchInput.textChanged.connect(self.filter_data)
        self.roastFilter.currentTextChanged.connect(self.filter_data)
        self.typeFilter.currentTextChanged.connect(self.filter_data)

        self.addButton = QPushButton("Добавить")
        self.horizontalLayout.addWidget(self.addButton)
        self.editButton = QPushButton("Редактировать")
        self.horizontalLayout.addWidget(self.editButton)
        self.deleteButton = QPushButton("Удалить")
        self.horizontalLayout.addWidget(self.deleteButton)

        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)
        self.deleteButton.clicked.connect(self.delete_coffee)

    def load_coffee_data(self, query=None, params=None):
        try:
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
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

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

    def add_coffee(self):
        dialog = AddEditCoffeeForm(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            cursor = self.conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO coffee (name, roast_degree, ground_whole, taste_description, price, volume)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['name'], data['roast_degree'], data['ground_whole'],
                      data['taste_description'], data['price'], data['volume']))
                self.conn.commit()
                self.load_coffee_data()
                QMessageBox.information(self, "Успех", "Кофе успешно добавлен")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Ошибка", "Кофе с таким названием уже существует")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def edit_coffee(self):
        selected = self.coffeeTable.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите кофе для редактирования")
            return
        coffee_id = int(self.coffeeTable.item(selected, 0).text())
        dialog = AddEditCoffeeForm(self, coffee_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            cursor = self.conn.cursor()
            try:
                cursor.execute('''
                    UPDATE coffee 
                    SET name=?, roast_degree=?, ground_whole=?, taste_description=?, price=?, volume=?
                    WHERE id=?
                ''', (data['name'], data['roast_degree'], data['ground_whole'],
                      data['taste_description'], data['price'], data['volume'], coffee_id))
                self.conn.commit()
                self.load_coffee_data()
                QMessageBox.information(self, "Успех", "Кофе успешно обновлен")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Ошибка", "Кофе с таким названием уже существует")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def delete_coffee(self):
        selected = self.coffeeTable.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите кофе для удаления")
            return
        coffee_name = self.coffeeTable.item(selected, 1).text()
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить '{coffee_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            coffee_id = int(self.coffeeTable.item(selected, 0).text())
            cursor = self.conn.cursor()
            try:
                cursor.execute('DELETE FROM coffee WHERE id=?', (coffee_id,))
                self.conn.commit()
                self.load_coffee_data()
                QMessageBox.information(self, "Успех", "Кофе успешно удален")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())