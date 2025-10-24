from PyQt5 import QtWidgets, QtCore
from .database import db

class RecentlyJoinedWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_recently_joined()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        # Title row with refresh button
        title_row = QtWidgets.QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)
        title = QtWidgets.QLabel("<b>ورودی های جدید</b>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-family: 'Dubai Medium'; color: #333; border-radius:16px;")
        # Refresh button
        self.refresh_btn = QtWidgets.QPushButton("🔄")
        self.refresh_btn.setFixedSize(32, 32)
        self.refresh_btn.setStyleSheet("font-size: 15pt; background: transparent; color: #333; border-radius: 16px;")
        self.refresh_btn.clicked.connect(self.load_recently_joined)
        title_row.addWidget(title, 1)
        title_row.addWidget(self.refresh_btn, 0, QtCore.Qt.AlignRight)
        layout.addLayout(title_row)
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setStyleSheet("font-size: 13pt; font-family: 'B Yekan';")
        layout.addWidget(self.list_widget)

        self.screensaver_btn = QtWidgets.QPushButton("اسکرین سیور")
        self.screensaver_btn.setStyleSheet("font-size: 15pt; background: #222; color: #fff; border-radius: 12px; padding: 10px 24px;")
        layout.addWidget(self.screensaver_btn)

        self.screensaver_btn.clicked.connect(self.on_screensaver_clicked)

    def on_screensaver_clicked(self):
        if hasattr(self.parent(), 'show_screensaver'):
            self.parent().show_screensaver()
        elif hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'show_screensaver'):
            self.parent().parent().show_screensaver()

    def load_recently_joined(self):
        self.list_widget.clear()
        members = db.get_members()
        for member in members:
            m = dict(member)
            display = f"{m['name']} {m['family']} | کد: {m['id']}"
            item = QtWidgets.QListWidgetItem(display)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.list_widget.addItem(item)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = RecentlyJoinedWidget()
    w.show()
    sys.exit(app.exec_())
