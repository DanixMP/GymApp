from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import os
import csv
import json
import shutil
from datetime import datetime, timedelta
from .database import db

class CustomMessageBox(QtWidgets.QDialog):
    def __init__(self, parent=None, title="", message="", status="success"):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Main Layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Container Frame
        container = QtWidgets.QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 2px solid #eee;
            }
        """)
        container_layout = QtWidgets.QVBoxLayout(container)
        
        # Icon and Title Layout
        title_layout = QtWidgets.QHBoxLayout()
        
        # Icon Label
        icon_label = QtWidgets.QLabel()
        icon_size = 48
        if status == "success":
            color = "#009966"
            icon = "✓"
        elif status == "error":
            color = "#d32f2f"
            icon = "✕"
        else:
            color = "#ff9800"
            icon = "!"
            
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: {color}22;
                border-radius: {icon_size//2}px;
                font-size: 32px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        icon_label.setFixedSize(icon_size, icon_size)
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setText(icon)
        
        # Title Label
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Dubai Medium';
                margin-right: 15px;
            }
        """)
        
        title_layout.addWidget(icon_label, alignment=QtCore.Qt.AlignRight)
        title_layout.addWidget(title_label, alignment=QtCore.Qt.AlignRight)
        title_layout.addStretch()
        
        # Message Label
        message_label = QtWidgets.QLabel(message)
        message_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 18px;
                font-family: 'Dubai Medium';
            }
        """)
        message_label.setWordWrap(True)
        message_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # OK Button
        ok_btn = QtWidgets.QPushButton("تایید")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 36px;
                font-size: 16px;
                font-family: 'Dubai Medium';
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """)
        ok_btn.clicked.connect(self.accept)
        
        # Add all widgets to container layout
        container_layout.addLayout(title_layout)
        container_layout.addWidget(message_label)
        container_layout.addWidget(ok_btn, alignment=QtCore.Qt.AlignCenter)
        
        # Add container to main layout
        layout.addWidget(container)
        
        # Set fixed size
        self.setFixedSize(400, 250)

class PaymentCard(QtWidgets.QWidget):
    def __init__(self, payment, parent_widget, parent=None):
        super().__init__(parent)
        self.payment = payment
        self.parent_widget = parent_widget
        self.form_visible = False
        self.init_ui()

    def init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        # Payment info card
        self.card_content = QtWidgets.QWidget()
        card_layout = QtWidgets.QVBoxLayout(self.card_content)
        
        # Format payment date (Jalali, robust fallback)
        from .date_utils import format_jalali_date
        payment_date_raw = self.payment['payment_date'] if 'payment_date' in self.payment.keys() else None
        if not payment_date_raw or payment_date_raw in (None, '', 'NULL'):
            payment_date_raw = self.payment['created_at'] if 'created_at' in self.payment.keys() else None
        if not payment_date_raw or payment_date_raw in (None, '', 'NULL'):
            payment_date_raw = self.payment['due_date'] if 'due_date' in self.payment.keys() else None
        if not payment_date_raw or payment_date_raw in (None, '', 'NULL'):
            from datetime import datetime
            payment_date_raw = datetime.now().strftime('%Y-%m-%d')
        formatted_date = format_jalali_date(payment_date_raw)
        
        # Get member info
        member_name = f"{self.payment['member_name'] if 'member_name' in self.payment.keys() else ''} {self.payment['member_family'] if 'member_family' in self.payment.keys() else ''}"
        if not member_name.strip():
            member_name = f"عضو {self.payment['member_id'] if 'member_id' in self.payment.keys() else 'نامشخص'}"
        
        # Format amount
        amount = self.payment['amount'] if 'amount' in self.payment.keys() else 0
        formatted_amount = f"{amount:,}" if amount else "0"
        
        # Payment status
        status = self.payment['status'] if 'status' in self.payment.keys() else 'paid'
        status_text = {
            'paid': 'پرداخت شده',
            'pending': 'در انتظار',
            'overdue': 'معوقه'
        }.get(status, status)
        
        # Status color
        status_color = {
            'paid': '#009966',
            'pending': '#ff9800',
            'overdue': '#d32f2f'
        }.get(status, '#666')
        
        info = f"""
        <div style='color:black; font-size:18pt; font-family: "Dubai Medium"; font-weight:bold;'>{member_name}</div>
        <div style='color:black; font-size:14pt; font-family: "B Yekan";'>مبلغ: {formatted_amount} تومان</div>
        <div style='color:black; font-size:12pt; font-family: "B Yekan";'>تاریخ پرداخت: {formatted_date}</div>
        <div style='color:{status_color}; font-size:12pt; font-family: "Dubai Medium"; font-weight:bold;'>وضعیت: {status_text}</div>
        <div style='color:#666; font-size:11pt; font-family: "Dubai Medium";'>توضیحات: {self.payment['description'] if 'description' in self.payment.keys() else '-'}</div>
        """
        
        info_label = QtWidgets.QLabel(info)
        info_label.setTextFormat(QtCore.Qt.RichText)
        info_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        info_label.setStyleSheet("font-family: 'B Yekan'; padding: 10px;")
        card_layout.addWidget(info_label)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        edit_btn = QtWidgets.QPushButton("ویرایش")
        delete_btn = QtWidgets.QPushButton("حذف")
        
        for btn in (edit_btn, delete_btn):
            btn.setStyleSheet("color: white; font-family: 'B Yekan'; background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(51, 153, 255, 255), stop:0.55 rgba(102, 0, 255, 255), stop:0.98 rgba(255, 0, 255, 255), stop:1 rgba(0, 0, 0, 0)); border-radius: 8px; font-size: 12pt; padding: 6px 18px;")
        
        delete_btn.setStyleSheet("background: #d32f2f; color: white; font-size: 12pt; font-family: 'B Yekan'; border-radius: 8px; padding: 6px 18px;")
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        card_layout.addLayout(btn_layout)
        
        self.edit_form = QtWidgets.QWidget()
        edit_layout = QtWidgets.QVBoxLayout(self.edit_form)
        form_layout = QtWidgets.QFormLayout()
        
        self.edit_amount = QtWidgets.QLineEdit(str(self.payment['amount'] if 'amount' in self.payment.keys() else ''))
        self.edit_description = QtWidgets.QLineEdit(self.payment['description'] if 'description' in self.payment.keys() else '')
        self.edit_status = QtWidgets.QComboBox()
        self.edit_status.addItems(['paid', 'pending', 'overdue'])
        self.edit_status.setCurrentText(self.payment['status'] if 'status' in self.payment.keys() else 'paid')
        
        for inp in [self.edit_amount, self.edit_description]:
            inp.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'B Yekan';")
        
        self.edit_status.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'B Yekan';")
        
        form_layout.addRow("مبلغ:", self.edit_amount)
        form_layout.addRow("توضیحات:", self.edit_description)
        form_layout.addRow("وضعیت:", self.edit_status)
        
        edit_layout.addLayout(form_layout)
        
        # Edit form buttons
        edit_btn_layout = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("ذخیره تغییرات")
        cancel_btn = QtWidgets.QPushButton("انصراف")
        
        save_btn.setStyleSheet("background: #009966; color: white; font-size: 12pt; font-family: 'B Yekan'; border-radius: 8px; padding: 8px 16px;")
        cancel_btn.setStyleSheet("background: #888; color: white; font-size: 12pt; font-family: 'B Yekan'; border-radius: 8px; padding: 8px 16px;")
        
        edit_btn_layout.addWidget(save_btn)
        edit_btn_layout.addWidget(cancel_btn)
        edit_layout.addLayout(edit_btn_layout)
        
        self.edit_form.hide()
        
        self.main_layout.addWidget(self.card_content)
        self.main_layout.addWidget(self.edit_form)
        
        self.setStyleSheet("QWidget { background: rgba(255,255,255,100); border-radius: 18px; padding: 18px; font-family: 'B Yekan'; }")
        
        edit_btn.clicked.connect(self.show_edit_form)
        delete_btn.clicked.connect(self.delete_payment)
        save_btn.clicked.connect(self.save_changes)
        cancel_btn.clicked.connect(self.hide_edit_form)

    def show_edit_form(self):
        self.card_content.hide()
        self.edit_form.show()

    def hide_edit_form(self):
        self.edit_form.hide()
        self.card_content.show()

    def save_changes(self):
        try:
            amount = float(self.edit_amount.text().strip())
            description = self.edit_description.text().strip()
            status = self.edit_status.currentText()
            
            # Get admin name from parent widget
            admin_name = getattr(self.parent_widget, 'admin_name', None)
            if admin_name:
                admin_info = f" (دریافت توسط: {admin_name})"
                if admin_info not in description:
                    description += admin_info
            
            from .database import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE transactions 
                    SET amount = ?, description = ?
                    WHERE id = ?
                """, (amount, description, self.payment['transaction_id']))
                cursor.execute("""
                    UPDATE member_payments 
                    SET status = ?
                    WHERE id = ?
                """, (status, self.payment['id']))
                conn.commit()

            self.hide_edit_form()
            self.parent_widget.load_payments()
            
        except ValueError:
            popup = CustomMessageBox(
                self, "خطا در ورودی",
                "لطفا مبلغ را به صورت عددی وارد کنید.",
                "error"
            )
            popup.exec_()
        except Exception as e:
            popup = CustomMessageBox(
                self, "خطا",
                f"ذخیره تغییرات با خطا مواجه شد:\n{str(e)}",
                "error"
            )
            popup.exec_()

    def delete_payment(self):
        confirm_dialog = CustomMessageBox(
            self, "تایید حذف",
            "آیا از حذف این پرداخت اطمینان دارید؟",
            "warning"
        )
        if confirm_dialog.exec_() == QtWidgets.QDialog.Accepted:
            try:
                from .database import db
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM member_payments WHERE id = ?", (self.payment['id'],))
                    cursor.execute("DELETE FROM transactions WHERE id = ?", (self.payment['transaction_id'],))
                    conn.commit()
                
                self.parent_widget.load_payments()
                
            except Exception as e:
                popup = CustomMessageBox(
                    self, "خطا",
                    f"حذف پرداخت با خطا مواجه شد:\n{str(e)}",
                    "error"
                )
                popup.exec_()


class PaymentWidget(QtWidgets.QWidget):
    def refresh(self):
        """Public method to reload payments and update statistics."""
        self.load_payments()
    def __init__(self, parent=None, total_members=0, admin_name=None):
        super().__init__(parent)
        self.total_members = total_members
        self.form_visible = False
        self.admin_name = admin_name
        self.init_ui()
        self.load_payments()

    def set_admin_name(self, admin_name):
        self.admin_name = admin_name

    def set_member_count(self, count):
        self.total_members = count

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Top bar
        top_bar = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("<div style='color:white; font-family: \"Dubai Medium\"; font-size: 32pt; font-weight: bold;'>امور مالی</div><div style='color:white; font-family: \"Dubai Medium\"; font-size: 18pt;'>مدیریت پرداخت‌ها و درآمدها</div>")
        title.setTextFormat(QtCore.Qt.RichText)
        top_bar.addWidget(title)
        top_bar.addStretch()

        # Backup button
        backup_btn = QtWidgets.QPushButton("💾 پشتیبان‌گیری و خروجی")
        backup_btn.setFixedHeight(70)
        backup_btn.setStyleSheet("background: #2c6e49; color: #fff; font-weight: bold; border-radius: 8px; padding: 0 18px; font-size: 13pt; font-family: 'Dubai Medium'; margin-left: 12px;")
        backup_btn.clicked.connect(self.show_export_dialog)
        top_bar.addWidget(backup_btn)

        refresh_btn = QtWidgets.QPushButton("🔄 بروزرسانی")
        refresh_btn.setFixedHeight(70)
        refresh_btn.setStyleSheet("background: #3c096c; color: #fff; font-weight: bold; border-radius: 8px; padding: 0 18px; font-size: 13pt; font-family: 'Dubai Medium'; margin-left: 12px;")
        refresh_btn.clicked.connect(self.refresh)
        top_bar.addWidget(refresh_btn)

        add_payment_btn = QtWidgets.QPushButton("+ افزودن پرداخت جدید")
        add_payment_btn.setFixedHeight(70)
        add_payment_btn.setStyleSheet("background: #009966; color: #fff; font-weight: bold; border-radius: 8px; padding: 0 16px; font-size: 13pt; font-family: 'Dubai Medium';")
        top_bar.addWidget(add_payment_btn)

        main_layout.addLayout(top_bar)
        
        # Add Payment Form (hidden by default)
        self.add_form = QtWidgets.QFrame()
        self.add_form.setStyleSheet("background: rgba(255,255,255,0.95); border-radius: 18px; padding: 18px; font-family: 'Dubai Medium';")
        self.add_form.setMaximumHeight(0)
        
        form_layout = QtWidgets.QFormLayout(self.add_form)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setFormAlignment(QtCore.Qt.AlignRight)
        
        # Form fields
        self.input_member_id = QtWidgets.QLineEdit()
        self.input_amount = QtWidgets.QLineEdit()
        self.input_description = QtWidgets.QLineEdit()
        self.input_payment_date = QtWidgets.QDateEdit()
        self.input_payment_date.setDate(QtCore.QDate.currentDate())
        self.input_payment_date.setCalendarPopup(True)
        
        self.input_member_id.setPlaceholderText("کد عضویت")
        self.input_amount.setPlaceholderText("مبلغ (تومان)")
        self.input_description.setPlaceholderText("توضیحات")
        
        for inp in [self.input_member_id, self.input_amount, self.input_description]:
            inp.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'Dubai Medium'; min-width: 900px; width: 75%;")
        # Modern style for QDateEdit
        self.input_payment_date.setStyleSheet('''
            QDateEdit {
                font-size: 15pt;
                padding: 8px 16px;
                border-radius: 8px;
                font-family: 'Dubai Medium';
                min-width: 900px;
                width: 75%;
                background: #f7f7f7;
                color: #222;
                border: 2px solid #009966;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border-left: 1px solid #009966;
                background: #009966;
            }
            QDateEdit::down-arrow {
                width: 18px;
                height: 18px;
            }
            QCalendarWidget {
                background: #fff;
                color: #222;
                border-radius: 12px;
                border: 1.5px solid #009966;
                font-family: "Dubai Medium";
                font-size: 15pt;
            }
            QCalendarWidget QToolButton {
                background: #009966;
                color: #fff;
                border-radius: 8px;
                margin: 4px;
                font-size: 13pt;
            }
            QCalendarWidget QToolButton:hover {
                background: #00b377;
            }
            QCalendarWidget QMenu {
                background: #fff;
                color: #222;
            }
            QCalendarWidget QSpinBox {
                background: #f7f7f7;
                color: #222;
                border-radius: 6px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: #f7f7f7;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background: #fff;
                color: #222;
                selection-background-color: #009966;
                selection-color: #fff;
                border-radius: 6px;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #aaa;
            }
            QCalendarWidget QAbstractItemView:selected {
                background: #009966;
                color: #fff;
            }
        ''')
        
        label_style = "font-size: 15pt; font-family: 'Dubai Medium'; color: #444; padding: 8px; border-radius: 8px; background: #f7f7f7; min-width: 100px; text-align: right;"
        
        form_layout.addRow(self.input_member_id, QtWidgets.QLabel("کد عضویت:"))
        form_layout.itemAt(0, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        form_layout.addRow(self.input_amount, QtWidgets.QLabel("مبلغ:"))
        form_layout.itemAt(1, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        form_layout.addRow(self.input_description, QtWidgets.QLabel("توضیحات:"))
        form_layout.itemAt(2, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        form_layout.addRow(self.input_payment_date, QtWidgets.QLabel("تاریخ پرداخت:"))
        form_layout.itemAt(3, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        self.submit_btn = QtWidgets.QPushButton("ثبت پرداخت")
        self.submit_btn.setStyleSheet("background: #009966; color: #fff; font-weight: bold; border-radius: 8px; padding: 12px 24px; font-size: 16pt; font-family: 'Dubai Medium';")
        form_layout.addRow(self.submit_btn)
        
        main_layout.addWidget(self.add_form)
        
        # Animation for slide down
        self.form_anim = QtCore.QPropertyAnimation(self.add_form, b"maximumHeight")
        self.form_anim.setDuration(350)
        self.form_anim.setStartValue(0)
        self.form_anim.setEndValue(420)
        
        # Connect buttons
        add_payment_btn.clicked.connect(self.toggle_form)
        self.submit_btn.clicked.connect(self.submit_payment)
        
        # Search/filter section
        search_layout = QtWidgets.QHBoxLayout()
        
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("جستجو بر اساس نام عضو یا کد...")
        self.search_edit.setStyleSheet("color: white; background: rgba(255,255,255,0.08); border-radius: 8px; font-size: 15pt; padding: 8px 16px; font-family: 'Dubai Medium';")
        search_layout.addWidget(self.search_edit)
        
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["همه پرداخت‌ها", "پرداخت شده", "در انتظار", "معوقه"])
        self.filter_combo.setStyleSheet("color: white; background: rgba(255,255,255,45); border-radius: 8px; font-size: 15pt; font-family: 'Dubai Medium';")
        search_layout.addWidget(self.filter_combo)
        
        # Date range filter
        self.date_from = QtWidgets.QDateEdit()
        self.date_to = QtWidgets.QDateEdit()
        self.date_from.setDate(QtCore.QDate.currentDate().addDays(-30))
        self.date_to.setDate(QtCore.QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        self.date_to.setCalendarPopup(True)
        
        for date_edit in [self.date_from, self.date_to]:
            date_edit.setStyleSheet("color: white; background: rgba(255,255,255,45); border-radius: 8px; font-size: 13pt; font-family: 'Dubai Medium'; padding: 4px 8px;")
        
        search_layout.addWidget(QtWidgets.QLabel("از:"))
        search_layout.addWidget(self.date_from)
        search_layout.addWidget(QtWidgets.QLabel("تا:"))
        search_layout.addWidget(self.date_to)
        
        # Connect filters
        self.search_edit.textChanged.connect(self.filter_payments)
        self.filter_combo.currentTextChanged.connect(self.filter_payments)
        self.date_from.dateChanged.connect(self.filter_payments)
        self.date_to.dateChanged.connect(self.filter_payments)
        
        main_layout.addLayout(search_layout)
        
        # Statistics section
        stats_layout = QtWidgets.QHBoxLayout()
        
        self.total_income_label = QtWidgets.QLabel("کل درآمد: 0 تومان")
        self.total_income_label.setStyleSheet("color: white; font-size: 16pt; font-family: 'Dubai Medium'; background: rgba(0,153,102,0.8); padding: 10px 20px; border-radius: 10px;")
        stats_layout.addWidget(self.total_income_label)
        
        self.monthly_income_label = QtWidgets.QLabel("درآمد ماهانه: 0 تومان")
        self.monthly_income_label.setStyleSheet("color: white; font-size: 16pt; font-family: 'Dubai Medium'; background: rgba(51,153,255,0.8); padding: 10px 20px; border-radius: 10px;")
        stats_layout.addWidget(self.monthly_income_label)
        
        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)
        
        # Scroll area for payment cards
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.scroll.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll)

    def toggle_form(self):
        if self.form_visible:
            self.form_anim.setDirection(QtCore.QAbstractAnimation.Backward)
            self.form_anim.start()
            self.form_visible = False
        else:
            self.form_anim.setDirection(QtCore.QAbstractAnimation.Forward)
            self.form_anim.start()
            self.form_visible = True

    def submit_payment(self):
        member_id = self.input_member_id.text().strip()
        amount_text = self.input_amount.text().strip()
        description = self.input_description.text().strip()
        payment_date = self.input_payment_date.date().toString("yyyy-MM-dd")
        
        if not all([member_id, amount_text]):
            popup = CustomMessageBox(
                self, "خطا در ورودی",
                "لطفا کد عضویت و مبلغ را وارد کنید.",
                "error"
            )
            popup.exec_()
            return
        
        try:
            amount = float(amount_text)
        except ValueError:
            popup = CustomMessageBox(
                self, "خطا در ورودی",
                "لطفا مبلغ را به صورت عددی وارد کنید.",
                "error"
            )
            popup.exec_()
            return
        
        try:
            from .database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Check if member exists
            cursor.execute("SELECT id, name, family FROM members WHERE id = ?", (member_id,))
            member = cursor.fetchone()
            if not member:
                popup = CustomMessageBox(
                    self, "خطا در ورودی",
                    "عضو با این کد یافت نشد.",
                    "error"
                )
                popup.exec_()
                return
            
            # Prepare description with admin name
            admin_info = f" (دریافت توسط: {self.admin_name})" if self.admin_name else ""
            final_description = description if description else f"پرداخت عضویت {member[1]} {member[2]}"
            if admin_info and admin_info not in final_description:
                final_description += admin_info

            # Add transaction
            cursor.execute("""
                INSERT INTO transactions (transaction_type, amount, description, created_by, payment_date)
                VALUES (?, ?, ?, ?, ?)
            """, ('membership', amount, final_description, 1, payment_date))
            
            transaction_id = cursor.lastrowid
            
            # Add member payment
            due_date = (datetime.strptime(payment_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO member_payments (member_id, transaction_id, payment_date, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (member_id, transaction_id, payment_date, due_date, 'paid'))
            
            conn.commit()
            conn.close()
            
            # Clear form
            self.input_member_id.clear()
            self.input_amount.clear()
            self.input_description.clear()
            self.input_payment_date.setDate(QtCore.QDate.currentDate())
            
            self.toggle_form()
            self.load_payments()
            
            popup = CustomMessageBox(
                self, "ثبت موفق", 
                f"پرداخت جدید به مبلغ {amount:,} تومان با موفقیت ثبت شد.",
                "success"
            )
            popup.exec_()
            
        except Exception as e:
            popup = CustomMessageBox(
                self, "خطا",
                f"ثبت پرداخت با خطا مواجه شد:\n{str(e)}",
                "error"
            )
            popup.exec_()

    def load_payments(self, filter_text=None, status_filter=None, date_from=None, date_to=None):
        try:
            from .database import db
            conn = db.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query with filters
            query = """
                SELECT mp.*, t.amount, t.description, t.transaction_type, t.payment_date as trans_date,
                       m.name as member_name, m.family as member_family, m.id as member_id
                FROM member_payments mp
                JOIN transactions t ON mp.transaction_id = t.id
                JOIN members m ON mp.member_id = m.id
                WHERE 1=1
            """
            params = []
            
            if filter_text:
                query += " AND (m.name LIKE ? OR m.family LIKE ? OR m.id LIKE ?)"
                params.extend([f"%{filter_text}%"] * 3)
            
            if status_filter and status_filter != "همه پرداخت‌ها":
                status_map = {
                    "پرداخت شده": "paid",
                    "در انتظار": "pending", 
                    "معوقه": "overdue"
                }
                if status_filter in status_map:
                    query += " AND mp.status = ?"
                    params.append(status_map[status_filter])
            
            if date_from:
                query += " AND mp.payment_date >= ?"
                params.append(date_from)
            
            if date_to:
                query += " AND mp.payment_date <= ?"
                params.append(date_to)
            
            query += " ORDER BY mp.payment_date DESC"
            
            cursor.execute(query, params)
            payments = cursor.fetchall()
            
            # Calculate statistics
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type = 'membership'")
            total_income = cursor.fetchone()[0] or 0
            
            # Monthly income (current month)
            current_month = datetime.now().strftime("%Y-%m")
            cursor.execute("""
                SELECT SUM(amount) FROM transactions 
                WHERE transaction_type = 'membership' 
                AND strftime('%Y-%m', payment_date) = ?
            """, (current_month,))
            monthly_income = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Update statistics labels
            self.total_income_label.setText(f"کل درآمد: {total_income:,} تومان")
            self.monthly_income_label.setText(f"درآمد ماهانه: {monthly_income:,} تومان")
            
            # Clear old cards
            for i in reversed(range(self.cards_layout.count())):
                widget = self.cards_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Add payment cards
            for idx, payment in enumerate(payments):
                card = PaymentCard(payment, parent_widget=self, parent=self)
                row = idx // 2
                col = idx % 2
                self.cards_layout.addWidget(card, row, col)
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بارگذاری پرداخت‌ها با خطا مواجه شد: {e}")

    def filter_payments(self):
        filter_text = self.search_edit.text()
        status_filter = self.filter_combo.currentText()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        
        self.load_payments(filter_text, status_filter, date_from, date_to)

    def show_export_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("پشتیبان‌گیری و خروجی")
        dialog.setStyleSheet("background: #fff;")
        layout = QtWidgets.QVBoxLayout(dialog)

        # Backup database section
        backup_label = QtWidgets.QLabel("پشتیبان‌گیری از پایگاه داده:")
        backup_label.setStyleSheet("font-size: 14pt; font-family: 'Dubai Medium'; color: #333; margin-top: 10px;")
        layout.addWidget(backup_label)

        backup_btn = QtWidgets.QPushButton("ایجاد نسخه پشتیبان")
        backup_btn.setStyleSheet("background: #2c6e49; color: white; padding: 10px; border-radius: 5px; font-family: 'Dubai Medium';")
        backup_btn.clicked.connect(self.create_database_backup)
        layout.addWidget(backup_btn)

        # Export section
        export_label = QtWidgets.QLabel("خروجی‌گیری:")
        export_label.setStyleSheet("font-size: 14pt; font-family: 'Dubai Medium'; color: #333; margin-top: 20px;")
        layout.addWidget(export_label)

        # Export options
        export_options = QtWidgets.QHBoxLayout()

        export_csv_btn = QtWidgets.QPushButton("خروجی CSV")
        export_csv_btn.setStyleSheet("background: #3c096c; color: white; padding: 10px; border-radius: 5px; font-family: 'Dubai Medium';")
        export_csv_btn.clicked.connect(self.export_to_csv)
        export_options.addWidget(export_csv_btn)

        export_json_btn = QtWidgets.QPushButton("خروجی JSON")
        export_json_btn.setStyleSheet("background: #3c096c; color: white; padding: 10px; border-radius: 5px; font-family: 'Dubai Medium';")
        export_json_btn.clicked.connect(self.export_to_json)
        export_options.addWidget(export_json_btn)

        layout.addLayout(export_options)

        # Date range for export
        date_range = QtWidgets.QHBoxLayout()
        date_range.addWidget(QtWidgets.QLabel("بازه زمانی:"))
        
        self.export_date_from = QtWidgets.QDateEdit()
        self.export_date_to = QtWidgets.QDateEdit()
        self.export_date_from.setDate(QtCore.QDate.currentDate().addDays(-30))
        self.export_date_to.setDate(QtCore.QDate.currentDate())
        self.export_date_from.setCalendarPopup(True)
        self.export_date_to.setCalendarPopup(True)
        
        date_range.addWidget(QtWidgets.QLabel("از:"))
        date_range.addWidget(self.export_date_from)
        date_range.addWidget(QtWidgets.QLabel("تا:"))
        date_range.addWidget(self.export_date_to)
        
        layout.addLayout(date_range)

        dialog.setFixedSize(400, 300)
        dialog.exec_()

    def create_database_backup(self):
        try:
            from .database import db
            source_db = db.db_path
            backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'gym_backup_{timestamp}.db')
            
            shutil.copy2(source_db, backup_path)
            
            popup = CustomMessageBox(
                self, "پشتیبان‌گیری موفق",
                f"فایل پشتیبان با موفقیت در مسیر زیر ایجاد شد:\n{backup_path}",
                "success"
            )
            popup.exec_()
        except Exception as e:
            popup = CustomMessageBox(
                self, "خطا",
                f"خطا در ایجاد نسخه پشتیبان:\n{str(e)}",
                "error"
            )
            popup.exec_()

    def get_export_data(self):
        try:
            date_from = self.export_date_from.date().toString("yyyy-MM-dd")
            date_to = self.export_date_to.date().toString("yyyy-MM-dd")
            
            from .database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    m.name || ' ' || m.family as member_name,
                    m.id as member_id,
                    t.amount,
                    t.description,
                    mp.status,
                    mp.payment_date,
                    mp.due_date
                FROM member_payments mp
                JOIN transactions t ON mp.transaction_id = t.id
                JOIN members m ON mp.member_id = m.id
                WHERE mp.payment_date BETWEEN ? AND ?
                ORDER BY mp.payment_date DESC
            """
            
            cursor.execute(query, (date_from, date_to))
            data = cursor.fetchall()
            headers = ['نام عضو', 'کد عضویت', 'مبلغ', 'توضیحات', 'وضعیت', 'تاریخ پرداخت', 'تاریخ سررسید']
            
            return headers, data
        finally:
            conn.close()

    def export_to_csv(self):
        try:
            headers, data = self.get_export_data()
            
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "ذخیره فایل CSV",
                os.path.expanduser("~"),
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)
                
                popup = CustomMessageBox(
                    self, "خروجی CSV",
                    f"فایل CSV با موفقیت در مسیر زیر ایجاد شد:\n{file_path}",
                    "success"
                )
                popup.exec_()
                
        except Exception as e:
            popup = CustomMessageBox(
                self, "خطا",
                f"خطا در ایجاد فایل CSV:\n{str(e)}",
                "error"
            )
            popup.exec_()

    def export_to_json(self):
        try:
            headers, data = self.get_export_data()
            
            json_data = []
            for row in data:
                json_data.append(dict(zip(headers, row)))
            
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "ذخیره فایل JSON",
                os.path.expanduser("~"),
                "JSON Files (*.json)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                popup = CustomMessageBox(
                    self, "خروجی JSON",
                    f"فایل JSON با موفقیت در مسیر زیر ایجاد شد:\n{file_path}",
                    "success"
                )
                popup.exec_()
                
        except Exception as e:
            popup = CustomMessageBox(
                self, "خطا",
                f"خطا در ایجاد فایل JSON:\n{str(e)}",
                "error"
            )
            popup.exec_()


