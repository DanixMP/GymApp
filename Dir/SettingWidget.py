
from PyQt5 import QtWidgets, QtCore
from .database import db

class CustomMessageBox(QtWidgets.QDialog):
    def __init__(self, title, message, icon_type="info", parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 15px;
            }
            QLabel {
                font-family: 'Dubai Medium';
                color: #3c096c;
            }
            QPushButton {
                background-color: #009966;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'Dubai Medium';
                font-size: 14pt;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #00b377;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Icon and title row
        top_row = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel()
        if icon_type == "warning":
            icon_label.setText("⚠️")
            title_color = "#ff9800"
        elif icon_type == "error":
            icon_label.setText("❌")
            title_color = "#f44336"
        else:  # info
            icon_label.setText("ℹ️")
            title_color = "#009966"
        
        icon_label.setStyleSheet("font-size: 24pt;")
        top_row.addWidget(icon_label)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 18pt;
            font-weight: bold;
            color: {title_color};
        """)
        top_row.addWidget(title_label)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Message
        msg_label = QtWidgets.QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14pt;")
        msg_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        layout.addWidget(msg_label)

        # Button
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        ok_button = QtWidgets.QPushButton("تایید")
        ok_button.clicked.connect(self.accept)
        btn_layout.addWidget(ok_button)
        layout.addLayout(btn_layout)

class SettingWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()


    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        # Title label
        label = QtWidgets.QLabel("تنظیمات برنامه")
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        label.setStyleSheet("font-size: 28pt; color: #fff; font-family: 'Dubai Medium'; background: #3c096c; border-radius: 16px; padding: 18px 0; margin-bottom: 24px;")
        layout.addWidget(label)

        # --- Admin Setup Section ---
        admin_group = QtWidgets.QGroupBox("ثبت مدیر جدید")
        admin_group.setStyleSheet("QGroupBox { font-size: 18pt; color: #009966; font-family: 'Dubai Medium'; border: 2px solid #009966; border-radius: 12px; margin-top: 12px; background: #fff; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 13px; color: #fff; background: #009966; border-radius: 8px; font-size: 20pt; margin-bottom: 12px; }")
        admin_layout = QtWidgets.QGridLayout(admin_group)
        admin_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        admin_layout.setHorizontalSpacing(18)
        admin_layout.setVerticalSpacing(16)

        # Labels
        username_label = QtWidgets.QLabel("نام کاربری:")
        full_name_label = QtWidgets.QLabel("نام کامل:")
        password_label = QtWidgets.QLabel("رمز عبور:")
        for lbl in (username_label, full_name_label, password_label):
            lbl.setStyleSheet("font-size: 16pt; color: #3c096c; font-family: 'Dubai Medium'; min-width: 120px; text-align: right;")

        # Inputs
        self.admin_username_edit = QtWidgets.QLineEdit()
        self.admin_username_edit.setPlaceholderText("نام کاربری مدیر")
        self.admin_username_edit.setStyleSheet("font-size: 16pt; color: #009966; background: #f3f3f3; border-radius: 8px; padding: 8px 16px; font-family: 'Dubai Medium';")
        self.admin_fullname_edit = QtWidgets.QLineEdit()
        self.admin_fullname_edit.setPlaceholderText("نام کامل مدیر برای نمایش")
        self.admin_fullname_edit.setStyleSheet("font-size: 16pt; color: #009966; background: #f3f3f3; border-radius: 8px; padding: 8px 16px; font-family: 'Dubai Medium';")
        self.admin_pass_edit = QtWidgets.QLineEdit()
        self.admin_pass_edit.setPlaceholderText("رمز عبور جدید")
        self.admin_pass_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.admin_pass_edit.setStyleSheet("font-size: 16pt; color: #009966; background: #f3f3f3; border-radius: 8px; padding: 8px 16px; font-family: 'Dubai Medium';")

        # Add to grid: add empty space row at the top
        spacer = QtWidgets.QLabel("")
        admin_layout.addWidget(spacer, 0, 0, 1, 3)
        admin_layout.setRowMinimumHeight(0, 18)  # adjust height as needed
        admin_layout.addWidget(username_label, 1, 2)
        admin_layout.addWidget(self.admin_username_edit, 1, 1)
        admin_layout.addWidget(full_name_label, 2, 2)
        admin_layout.addWidget(self.admin_fullname_edit, 2, 1)
        admin_layout.addWidget(password_label, 3, 2)
        admin_layout.addWidget(self.admin_pass_edit, 3, 1)

        # Save button
        self.save_admin_btn = QtWidgets.QPushButton("ذخیره تنظیمات مدیر")
        self.save_admin_btn.setStyleSheet("font-size: 17pt; background: #009966; color: #fff; border-radius: 10px; padding: 10px 32px; margin-top: 18px;")
        self.save_admin_btn.clicked.connect(self.save_admin_settings)
        admin_layout.addWidget(self.save_admin_btn, 4, 1, 1, 2, alignment=QtCore.Qt.AlignCenter)

        layout.addWidget(admin_group)

        # --- Monthly Fee Section ---
        fee_group = QtWidgets.QGroupBox("تنظیم شهریه ماهانه پیش‌فرض")
        fee_group.setStyleSheet("QGroupBox { font-size: 18pt; color: #3c096c; font-family: 'Dubai Medium'; border: 2px solid #3c096c; border-radius: 12px; margin-top: 12px; background: #fff; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: #fff; background: #3c096c; border-radius: 8px; font-size: 20pt; margin-bottom: 12px; }")
        fee_layout = QtWidgets.QHBoxLayout(fee_group)
        fee_label = QtWidgets.QLabel("شهریه ماهانه (تومان):")
        fee_label.setStyleSheet("font-size: 16pt; color: #3c096c; font-family: 'Dubai Medium'; min-width: 180px;")
        self.fee_edit = QtWidgets.QLineEdit()
        self.fee_edit.setStyleSheet("font-size: 16pt; color: #009966; background: #f3f3f3; border-radius: 8px; padding: 8px 16px; font-family: 'Dubai Medium'; max-width: 180px;")
        self.fee_edit.setPlaceholderText("مثلاً 500000")
        # Load current fee from DB
        try:
            fee = db.get_monthly_fee()
            self.fee_edit.setText(str(fee))
        except Exception:
            self.fee_edit.setText("")
        self.save_fee_btn = QtWidgets.QPushButton("ذخیره شهریه")
        self.save_fee_btn.setStyleSheet("font-size: 15pt; background: #3c096c; color: #fff; border-radius: 10px; padding: 8px 24px;")
        self.save_fee_btn.clicked.connect(self.save_monthly_fee)
        fee_layout.addWidget(fee_label)
        fee_layout.addWidget(self.fee_edit)
        fee_layout.addWidget(self.save_fee_btn)
        layout.addWidget(fee_group)

        # --- Background Image Section ---
        bg_group = QtWidgets.QGroupBox("تغییر تصویر پس‌زمینه برنامه")
        bg_group.setStyleSheet("QGroupBox { font-size: 18pt; color: #3c096c; font-family: 'Dubai Medium'; border: 2px solid #3c096c; border-radius: 12px; margin-top: 12px; background: #fff; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: #fff; background: #3c096c; border-radius: 8px; font-size: 20pt; margin-bottom: 12px; }")
        bg_layout = QtWidgets.QHBoxLayout(bg_group)
        self.bg_select_btn = QtWidgets.QPushButton("انتخاب تصویر جدید")
        self.bg_select_btn.setStyleSheet("font-size: 15pt; background: #3c096c; color: #fff; border-radius: 10px; padding: 8px 24px;")
        self.bg_select_btn.clicked.connect(self.select_background_image)
        self.bg_default_btn = QtWidgets.QPushButton("بازگردانی پس‌زمینه پیش‌فرض")
        self.bg_default_btn.setStyleSheet("font-size: 15pt; background: #009966; color: #fff; border-radius: 10px; padding: 8px 24px;")
        self.bg_default_btn.clicked.connect(self.set_default_background)
        bg_layout.addWidget(self.bg_select_btn, 1)
        bg_layout.addWidget(self.bg_default_btn, 1)
        layout.addWidget(bg_group)


    def select_background_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "انتخاب تصویر پس‌زمینه", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            try:
                db.set_background_image(file_path)
            except Exception:
                pass
            mw = self.window()
            if mw:
                mw.setStyleSheet(f"QWidget {{ background-image: url('{file_path}'); background-repeat: no-repeat; background-position: center;}}")

    def set_default_background(self):
        try:
            db.set_background_image(None) 
        except Exception:
            pass
        mw = self.window()
        if mw:
            mw.setStyleSheet("")

    def save_monthly_fee(self):
        fee_text = self.fee_edit.text().strip()
        if not fee_text.isdigit() or int(fee_text) <= 0:
            CustomMessageBox("خطا", "لطفاً یک مبلغ معتبر برای شهریه ماهانه وارد کنید.", "warning", self).exec_()
            return
        try:
            db.set_monthly_fee(int(fee_text))
            CustomMessageBox("ذخیره شد", f"شهریه ماهانه جدید با موفقیت ذخیره شد: {fee_text} تومان", "info", self).exec_()
        except Exception as e:
            CustomMessageBox("خطا", f"خطا در ذخیره شهریه: {e}", "error", self).exec_()

    def save_admin_settings(self):
        username = self.admin_username_edit.text().strip()
        full_name = self.admin_fullname_edit.text().strip()
        password = self.admin_pass_edit.text().strip()
        if not username or not full_name or not password:
            CustomMessageBox("خطا", "لطفاً نام کاربری، نام کامل و رمز عبور را وارد کنید.", "warning", self).exec_()
            return
        # Try to save admin to database
        email = None  # No email field in UI, set as None
        result = db.create_user(username, password, full_name, email, role="admin")
        if result:
            CustomMessageBox("ذخیره شد", f"تنظیمات مدیر با موفقیت ذخیره شد.\nنام کامل: {full_name}", "info", self).exec_()
            self.admin_username_edit.clear()
            self.admin_fullname_edit.clear()
            self.admin_pass_edit.clear()
        else:
            CustomMessageBox("خطا", "نام کاربری یا ایمیل قبلاً ثبت شده است.", "warning", self).exec_()
