from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import sqlite3
from .database import db

class ExpiringMembersWidget(QtWidgets.QWidget):
    def get_expiring_count(self):
        """Return the number of expiring members currently shown in the list (excluding error item)."""
        count = 0
        for i in range(self.listWidget.count()):
            text = self.listWidget.item(i).text()
            if "خطا" not in text:
                count += 1
        return count
    def __init__(self, parent=None, days_left=7):
        super().__init__(parent)
        self.days_left = days_left
        self.init_ui()
        self.populate_expiring_members()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("<b>کاربران با کمتر از {} روز باقیمانده</b>".format(self.days_left))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16pt; color: #3c096c; font-family: 'B Yekan'; background: #fff; border-radius: 18px; padding: 8px;")
        layout.addWidget(title)
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setStyleSheet("font: 13pt 'B Yekan'; background: #f8f8ff; border-radius: 12px;")
        layout.addWidget(self.listWidget)

    def populate_expiring_members(self):
        try:
            rows = db.get_expiring_members(self.days_left)
            self.listWidget.clear()
            for row in rows:
                name = row.get('name', '')
                family = row.get('family', '')
                id_ = row.get('id', '')
                remaining = int(row.get('remaining_days', 0))
                item = QtWidgets.QListWidgetItem(f"{name} {family} | کد: {id_} | باقیمانده: {remaining} روز")
                item.setTextAlignment(Qt.AlignCenter)
                self.listWidget.addItem(item)
        except Exception as e:
            self.listWidget.clear()
            error_item = QtWidgets.QListWidgetItem("خطا در دریافت اطلاعات")
            error_item.setTextAlignment(Qt.AlignCenter)
            self.listWidget.addItem(error_item)
