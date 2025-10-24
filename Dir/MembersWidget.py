from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import os


class MemberCard(QtWidgets.QWidget):
    def __init__(self, member, parent_widget, parent=None):
        super().__init__(parent)
        self.member = member
        self.parent_widget = parent_widget
        self.form_visible = False
        # Get admin_name from parent_widget if available
        self.admin_name = getattr(parent_widget, 'admin_name', None)
        self.init_ui()

    def init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        # User info and buttons in one box, no icon
        remaining_days = self.member['remaining_days']
        remaining_days_text = f"{int(remaining_days)} روز باقی مانده" if remaining_days is not None and remaining_days >= 0 else "منقضی شده"
        # Regular card content
        self.card_content = QtWidgets.QWidget()
        card_layout = QtWidgets.QVBoxLayout(self.card_content)
        from .date_utils import format_jalali_date
        # Robust join date handling for sqlite3.Row
        join_date_raw = self.member['join_date'] if 'join_date' in self.member.keys() else None
        if not join_date_raw or join_date_raw in (None, '', 'NULL'):
            join_date_raw = self.member['created_at'] if 'created_at' in self.member.keys() else None
        if not join_date_raw or join_date_raw in (None, '', 'NULL'):
            from datetime import datetime
            join_date_raw = datetime.now().strftime('%Y-%m-%d')
        join_date = format_jalali_date(join_date_raw)
        info = f"""
        <div style='color:black; font-size:18pt; font-family: "B Yekan"; font-weight:bold;'>{self.member['name']} {self.member['family']}</div>
        <div style='color:black; font-size:12pt; font-family: "B Yekan";'>کد: {self.member['id'] or '-'}</div>
        <div style='color:black; font-size:12pt; font-family: "B Yekan";'>تلفن: {self.member['phone'] or '-'}</div>
        <div style='color:black; font-size:12pt; font-family: "B Yekan";'>تاریخ عضویت: {join_date}</div>
        <div style='color:black; font-size:12pt; font-family: "B Yekan";'>وضعیت عضویت: {remaining_days_text}</div>
        """
        info_label = QtWidgets.QLabel(info)
        info_label.setTextFormat(QtCore.Qt.RichText)
        info_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        info_label.setStyleSheet("font-family: 'B Yekan';")
        card_layout.addWidget(info_label)
        # Regular buttons
        btn_layout = QtWidgets.QHBoxLayout()
        renew_btn = QtWidgets.QPushButton("تمدید")
        edit_btn = QtWidgets.QPushButton("ویرایش")
        for btn in (renew_btn, edit_btn):
            btn.setStyleSheet("color: white; font-family: 'B Yekan'; background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(51, 153, 255, 255), stop:0.55 rgba(102, 0, 255, 255), stop:0.98 rgba(255, 0, 255, 255), stop:1 rgba(0, 0, 0, 0)); border-radius: 8px; font-size: 12pt; padding: 6px 18px;")
        btn_layout.addWidget(renew_btn)
        btn_layout.addWidget(edit_btn)
        card_layout.addLayout(btn_layout)
        # Create expanded edit form
        self.edit_form = QtWidgets.QWidget()
        edit_layout = QtWidgets.QVBoxLayout(self.edit_form)
        # Edit fields
        form_layout = QtWidgets.QFormLayout()
        self.edit_name = QtWidgets.QLineEdit(self.member['name'])
        self.edit_family = QtWidgets.QLineEdit(self.member['family'])
        self.edit_phone = QtWidgets.QLineEdit(self.member['phone'])
        self.edit_id = QtWidgets.QLineEdit(self.member['id'])
        self.edit_id.setEnabled(False)  # ID shouldn't be editable
        for inp in [self.edit_name, self.edit_family, self.edit_phone, self.edit_id]:
            inp.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'B Yekan';")
        form_layout.addRow("نام:", self.edit_name)
        form_layout.addRow("نام خانوادگی:", self.edit_family)
        form_layout.addRow("تلفن:", self.edit_phone)
        form_layout.addRow("کد عضویت:", self.edit_id)
        edit_layout.addLayout(form_layout)
        # Edit form buttons
        edit_btn_layout = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("ذخیره تغییرات")
        delete_btn = QtWidgets.QPushButton("حذف عضو")
        # cancel_btn = QtWidgets.QPushButton("انصراف")
        save_btn.setStyleSheet("background: #009966; color: white; font-size: 12pt; font-family: 'B Yekan'; border-radius: 8px; padding: 8px 16px;")
        delete_btn.setStyleSheet("background: #d32f2f; color: white; font-size: 12pt; font-family: 'B Yekan'; border-radius: 8px; padding: 8px 16px;")
        # cancel_btn.setStyleSheet("background: #888; color: white; font-size: 12pt; font-family: 'B Yekan'; border-radius: 8px; padding: 8px 16px;")
        edit_btn_layout.addWidget(save_btn)
        edit_btn_layout.addWidget(delete_btn)
        # edit_btn_layout.addWidget(cancel_btn)
        edit_layout.addLayout(edit_btn_layout)
        # Connect edit form buttons to their methods
        save_btn.clicked.connect(self.save_changes)
        delete_btn.clicked.connect(self.delete_member)
        # cancel_btn.clicked.connect(self.toggle_form)
        self.edit_form.hide()
        # Add widgets to main layout
        self.main_layout.addWidget(self.card_content)
        self.main_layout.addWidget(self.edit_form)
        # Ensure card content is visible by default
        self.card_content.show()
        self.edit_form.hide()
        # Setup form animation
        self.form_anim = QtCore.QPropertyAnimation(self.edit_form, b"maximumHeight")
        self.form_anim.setDuration(200)
        self.form_anim.setStartValue(0)
        self.form_anim.setEndValue(400)
        self.setStyleSheet("QWidget { background: rgba(255,255,255,100); border-radius: 18px; padding: 18px; font-family: 'B Yekan'; }")
        # Connect buttons
        renew_btn.clicked.connect(self.renew_membership)
        edit_btn.clicked.connect(self.show_edit_form)
    def show_edit_form(self):
        # Populate edit fields with current member data
        self.edit_name.setText(self.member['name'])
        self.edit_family.setText(self.member['family'])
        self.edit_phone.setText(self.member['phone'])
        self.edit_id.setText(self.member['id'])
        # Show the edit form with animation
        if not self.form_visible:
            self.form_anim.setDirection(QtCore.QAbstractAnimation.Forward)
            self.form_anim.start()
            self.form_visible = True
        self.edit_form.show()
        self.card_content.hide()

    def toggle_form(self):
        if self.form_visible:
            self.form_anim.setDirection(QtCore.QAbstractAnimation.Backward)
            self.form_anim.start()
            self.form_visible = False
        else:
            self.form_anim.setDirection(QtCore.QAbstractAnimation.Forward)
            self.form_anim.start()
            self.form_visible = True

    def renew_membership(self):
        from .database import db
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            # Get default monthly fee from settings
            cursor.execute("SELECT value FROM settings WHERE key = 'monthly_fee'")
            monthly_fee_result = cursor.fetchone()
            monthly_fee = float(monthly_fee_result[0]) if monthly_fee_result else 750000
            # Check if the user has an end_date
            cursor.execute("SELECT end_date FROM members WHERE id = ?", (self.member['id'],))
            end_date = cursor.fetchone()
            from datetime import datetime, timedelta
            if end_date and end_date[0]:
                # Add 30 days to the existing end_date
                new_end_date = (datetime.strptime(end_date[0], "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
            else:
                # Set end_date to today + 30 days
                new_end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            cursor.execute("UPDATE members SET end_date = ? WHERE id = ?", (new_end_date, self.member['id']))
            # Add transaction record for the renewal
            member_name = f"{self.member['name']} {self.member['family']}"
            admin_info = f" توسط {self.admin_name}" if self.admin_name else ""
            description = f"تمدید عضویت {member_name}{admin_info}"
            cursor.execute("""
                INSERT INTO transactions (transaction_type, amount, description, created_by, payment_date)
                VALUES (?, ?, ?, ?, date('now'))
            """, ('membership', monthly_fee, description, 1))
            transaction_id = cursor.lastrowid
            # Add member payment record
            cursor.execute("""
                INSERT INTO member_payments (member_id, transaction_id, payment_date, due_date, status)
                VALUES (?, ?, date('now'), ?, 'paid')
            """, (self.member['id'], transaction_id, new_end_date))
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"تمدید عضویت با خطا مواجه شد: {e}")
        finally:
            conn.close()
        try:
            self.parent_widget.load_members()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بروزرسانی لیست اعضا با خطا مواجه شد: {e}")
    
    def save_changes(self):
        name = self.edit_name.text().strip()
        family = self.edit_family.text().strip()
        phone = self.edit_phone.text().strip()
        if not all([name, family, phone]):
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفا همه فیلدها را پر کنید.")
            return
        from .database import db
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE members 
                SET name = ?, family = ?, phone = ?
                WHERE id = ?
            """, (name, family, phone, self.member['id']))
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"ذخیره تغییرات با خطا مواجه شد: {e}")
            return
        finally:
            try:
                conn.close()
            except:
                pass
        try:
            self.toggle_form()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بستن فرم ویرایش با خطا مواجه شد: {e}")
        try:
            self.parent_widget.load_members()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بروزرسانی لیست اعضا با خطا مواجه شد: {e}")

    def delete_member(self):
        # Show confirmation dialog
        reply = QtWidgets.QMessageBox.question(
            self,
            "تایید حذف",
            "آیا از حذف این عضو اطمینان دارید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            from .database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            try:
                # Gather related transaction ids, then delete dependent rows
                cursor.execute("SELECT transaction_id FROM member_payments WHERE member_id = ?", (self.member['id'],))
                tx_ids = [row[0] for row in cursor.fetchall() if row and row[0] is not None]
                cursor.execute("DELETE FROM member_payments WHERE member_id = ?", (self.member['id'],))
                if tx_ids:
                    placeholders = ",".join(["?"] * len(tx_ids))
                    cursor.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", tx_ids)
                cursor.execute("DELETE FROM members WHERE id = ?", (self.member['id'],))
                conn.commit()
                try:
                    self.parent_widget.load_members()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "خطا", f"بروزرسانی لیست اعضا با خطا مواجه شد: {e}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "خطا", f"حذف عضو با خطا مواجه شد: {e}")
            finally:
                conn.close()

class MembersWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None, admin_name=None):
        super().__init__(parent)
        self.main_window = main_window
        self.form_visible = False
        self.admin_name = admin_name
        self.init_ui()
        self.load_members()
        
    def set_admin_name(self, admin_name):
        self.admin_name = admin_name

    def toggle_form(self):
        if self.form_visible:
            self.form_anim.setDirection(QtCore.QAbstractAnimation.Backward)
            self.form_anim.start()
            self.form_visible = False
        else:
            self.form_anim.setDirection(QtCore.QAbstractAnimation.Forward)
            self.form_anim.start()
            self.form_visible = True

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        # Top bar
        top_bar = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("<div style='color:white; font-family: \"Dubai Medium\"; font-size: 32pt; font-weight: bold;'>ورزشکاران</div><div style='color:white; font-family: \"Dubai Medium\"; font-size: 18pt;'>مدیریت ورزشکاران و عضویت‌ها</div>")
        title.setTextFormat(QtCore.Qt.RichText)
        top_bar.addWidget(title)
        top_bar.addStretch()
        add_btn = QtWidgets.QPushButton("+ افزودن ورزشکار جدید")
        add_btn.setFixedHeight(70)
        add_btn.setStyleSheet("background: #009966; color: #fff; font-weight: bold; border-radius: 8px; padding: 0 16px; font-size: 13pt;")
        top_bar.addWidget(add_btn)
        main_layout.addLayout(top_bar)
        # Add Member Form (hidden by default)
        self.add_form = QtWidgets.QFrame()
        self.add_form.setStyleSheet("background: rgba(255,255,255,0.95); border-radius: 18px; padding: 18px; font-family: 'Dubai Medium';")
        self.add_form.setMaximumHeight(0)
        form_layout = QtWidgets.QFormLayout(self.add_form)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setFormAlignment(QtCore.Qt.AlignRight)
        self.input_name = QtWidgets.QLineEdit()
        self.input_family = QtWidgets.QLineEdit()
        self.input_phone = QtWidgets.QLineEdit()
        self.input_id = QtWidgets.QLineEdit()
        self.gender_group = QtWidgets.QButtonGroup(self.add_form)
        self.gender_man = QtWidgets.QRadioButton("مرد")
        self.gender_man.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'Dubai Medium'; min-width: 900px; width: 75%; min-height: 30px;")
        self.gender_woman = QtWidgets.QRadioButton("زن")
        self.gender_woman.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'Dubai Medium'; min-width: 900px; width: 75%; min-height: 30px;")
        self.gender_group.addButton(self.gender_man)
        self.gender_group.addButton(self.gender_woman)
        self.input_name.setPlaceholderText("نام")
        self.input_family.setPlaceholderText("نام خانوادگی")
        self.input_phone.setPlaceholderText("تلفن")
        self.input_id.setPlaceholderText("کد عضویت")
        for inp in [self.input_name, self.input_family, self.input_phone, self.input_id]:
            inp.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'Dubai Medium'; min-width: 900px; width: 75%;")
        label_style = "font-size: 15pt; font-family: 'Dubai Medium'; color: #444; padding: 8px; border-radius: 8px; background: #f7f7f7; min-width: 100px; text-align: right;"
        form_layout.addRow(self.input_name, QtWidgets.QLabel("نام:"))
        form_layout.itemAt(0, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        form_layout.addRow(self.input_family, QtWidgets.QLabel("نام خانوادگی:"))
        form_layout.itemAt(1, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        form_layout.addRow(self.input_phone, QtWidgets.QLabel("تلفن:"))
        form_layout.itemAt(2, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        form_layout.addRow(self.input_id, QtWidgets.QLabel("کد عضویت:"))
        form_layout.itemAt(3, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)

        # Add join date field
        from .date_utils import get_current_jalali_date
        self.join_date = QtWidgets.QLineEdit(get_current_jalali_date())
        self.join_date.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'Dubai Medium'; min-width: 900px; width: 75%;")
        form_layout.addRow(self.join_date, QtWidgets.QLabel("تاریخ عضویت:"))
        form_layout.itemAt(4, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)

        # Add membership days field
        self.membership_days = QtWidgets.QLineEdit()
        self.membership_days.setPlaceholderText("تعداد روز عضویت (پیش‌فرض ۳۰)")
        self.membership_days.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'Dubai Medium'; min-width: 900px; width: 75%;")
        form_layout.addRow(self.membership_days, QtWidgets.QLabel("تعداد روز عضویت:"))
        form_layout.itemAt(5, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)

        gender_layout = QtWidgets.QHBoxLayout()
        gender_layout.setAlignment(QtCore.Qt.AlignLeft)
        gender_layout.addWidget(self.gender_man)
        gender_layout.addWidget(self.gender_woman)

        gender_label = QtWidgets.QLabel("جنسیت:")
        gender_label.setStyleSheet(label_style)
        gender_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        gender_label.setLayoutDirection(QtCore.Qt.RightToLeft)

        gender_widget = QtWidgets.QWidget()
        gender_widget.setLayout(gender_layout)
        gender_widget.setLayoutDirection(QtCore.Qt.LeftToRight)

        self.gender_man.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gender_woman.setLayoutDirection(QtCore.Qt.LeftToRight)

        # Add gender widget and label to form layout
        form_layout.addRow(gender_widget, gender_label)
        self.submit_btn = QtWidgets.QPushButton("ثبت ورزشکار")
        self.submit_btn.setStyleSheet("background: #009966; color: #fff; font-weight: bold; border-radius: 8px; padding: 12px 24px; font-size: 16pt; font-family: 'Dubai Medium';")
        form_layout.addRow(self.submit_btn)
        main_layout.addWidget(self.add_form)
        # Animation for slide down
        self.form_anim = QtCore.QPropertyAnimation(self.add_form, b"maximumHeight")
        self.form_anim.setDuration(350)
        self.form_anim.setStartValue(0)
        self.form_anim.setEndValue(520)  # Increased height for better look
        self.form_visible = False
        add_btn.clicked.connect(self.toggle_form)
        self.submit_btn.clicked.connect(self.submit_member)

        search_layout = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("جستجو بر اساس نام یا شماره...")
        self.search_edit.setStyleSheet("color: white; background: rgba(255,255,255,0.08); border-radius: 8px; font-size: 15pt; padding: 8px 16px; font-family: 'Dubai Medium';")
        search_layout.addWidget(self.search_edit)
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItem("همه ورزشکاران")
        self.filter_combo.setStyleSheet("color: white; text-align: center; background: rgba(255,255,255,45); border-radius: 8px; font-size: 15pt; font-family: 'Dubai Medium';")
        search_layout.addWidget(self.filter_combo)
        self.search_edit.textChanged.connect(self.filter_members)
        main_layout.addLayout(search_layout)
        # Scroll area for cards
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.scroll.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll)

    def show_custom_warning(self, title, message):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setStyleSheet(
            "QMessageBox { font-size: 14pt; font-family: 'Dubai Medium'; background-color: #f7f7f7; border-radius: 12px; }"
            "QLabel { color: #444; padding: 8px; }"
            "QPushButton { background-color: #009966; color: white; font-size: 12pt; border-radius: 8px; padding: 6px 12px; }"
        )
        msg_box.exec_()

    # Removed duplicate/old submit_member definition to ensure only the correct one is used
    def submit_member(self):
        name = self.input_name.text().strip()
        family = self.input_family.text().strip()
        phone = self.input_phone.text().strip()
        id_ = self.input_id.text().strip()
        gender = None
        if self.gender_man.isChecked():
            gender = "مرد"
        elif self.gender_woman.isChecked():
            gender = "زن"
        join_date_str = self.join_date.text().strip()
        days_str = self.membership_days.text().strip()
        from .date_utils import jalali_to_gregorian, get_current_jalali_date
        if not (name and family and phone and id_ and gender and join_date_str):
            self.show_custom_warning("خطا", "لطفا همه فیلدها و جنسیت را پر کنید.")
            return
        # Convert Jalali join date to Gregorian
        gregorian_join_date = jalali_to_gregorian(join_date_str)
        if not gregorian_join_date:
            self.show_custom_warning("خطا", "تاریخ عضویت معتبر نیست. لطفا به فرمت صحیح (1402/01/01) وارد کنید.")
            return
        # Parse membership days, default to 30 if empty or invalid
        try:
            membership_days = int(days_str) if days_str else 30
            if membership_days <= 0:
                membership_days = 30
        except Exception:
            membership_days = 30
        from datetime import datetime, timedelta
        start_date = gregorian_join_date
        end_date = (datetime.strptime(gregorian_join_date, "%Y-%m-%d") + timedelta(days=membership_days)).strftime("%Y-%m-%d")
        from .database import db
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            # Insert with join_date, start_date, and end_date
            cursor.execute('INSERT INTO members (id, name, family, gender, phone, start_date, end_date, join_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                         (id_, name, family, gender, phone, start_date, end_date, gregorian_join_date))
            conn.commit()
        except Exception as e:
            self.show_custom_warning("خطا", f"ثبت ورزشکار جدید با خطا مواجه شد: {e}")
            return
        finally:
            try:
                conn.close()
            except:
                pass
        try:
            self.input_name.clear()
            self.input_family.clear()
            self.input_phone.clear()
            self.input_id.clear()
            self.join_date.setText(get_current_jalali_date())
            self.membership_days.clear()
            self.gender_man.setChecked(False)
            self.gender_woman.setChecked(False)
        except Exception as e:
            self.show_custom_warning("خطا", f"پاکسازی فرم با خطا مواجه شد: {e}")
        try:
            self.toggle_form()
        except Exception as e:
            self.show_custom_warning("خطا", f"بستن فرم با خطا مواجه شد: {e}")
        try:
            self.load_members()
        except Exception as e:
            self.show_custom_warning("خطا", f"بروزرسانی لیست اعضا با خطا مواجه شد: {e}")
        # Refresh payment area if available
        try:
            if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'paymentWidget'):
                self.main_window.paymentWidget.refresh()
        except Exception:
            pass

    def load_members(self, filter_text=None):
        from .database import db
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        base_query = """
            SELECT *, 
                CASE WHEN end_date IS NOT NULL THEN CAST(julianday(end_date) - julianday('now') AS INT) ELSE NULL END AS remaining_days,
                join_date
            FROM members
        """
        
        if filter_text:
            cursor.execute(f"{base_query} WHERE name LIKE ? OR family LIKE ? OR phone LIKE ? OR id LIKE ?", 
                         [f"%{filter_text}%"]*4)
        else:
            cursor.execute(base_query)
        members = cursor.fetchall()
        conn.close()
        # Clear old cards
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Add cards
        for idx, member in enumerate(members):
            card = MemberCard(member, parent_widget=self, parent=self)
            row = idx // 3
            col = idx % 3
            self.cards_layout.addWidget(card, row, col)

    def filter_members(self, text):
        self.load_members(text)

    def toggle_edit_form(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.edit_form.show()
            self.card_content.hide()
        else:
            self.edit_form.hide()
            self.card_content.show()

    def save_changes(self):
        name = self.edit_name.text().strip()
        family = self.edit_family.text().strip()
        phone = self.edit_phone.text().strip()
        if not all([name, family, phone]):
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفا همه فیلدها را پر کنید.")
            return
        from .database import db
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE members 
                SET name = ?, family = ?, phone = ?
                WHERE id = ?
            """, (name, family, phone, self.member['id']))
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"ذخیره تغییرات با خطا مواجه شد: {e}")
            return
        finally:
            try:
                conn.close()
            except:
                pass
        try:
            self.toggle_edit_form()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بستن فرم ویرایش با خطا مواجه شد: {e}")
        try:
            self.parent_widget.load_members()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بروزرسانی لیست اعضا با خطا مواجه شد: {e}")

    def delete_member(self):
        reply = QtWidgets.QMessageBox.question(
            self, 'تایید حذف',
            'آیا از حذف این عضو اطمینان دارید؟',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            from .database import db
            conn = db.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM members WHERE id = ?", (self.member['id'],))
                conn.commit()
                # Refresh the member list
                self.parent_widget.load_members()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "خطا", f"حذف عضو با خطا مواجه شد: {e}")
            finally:
                conn.close()

    def renew_membership(self):
        from .database import db
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            # Check if the user has a start_date
            cursor.execute("SELECT start_date FROM members WHERE id = ?", (self.member['id'],))
            start_date = cursor.fetchone()
            if start_date and start_date[0]:
                # Add 30 days to the existing start_date
                cursor.execute("UPDATE members SET start_date = date(julianday(start_date), '+30 days') WHERE id = ?", (self.member['id'],))
            else:
                # Set start_date to today and add 30 days
                cursor.execute("UPDATE members SET start_date = date('now', '+30 days') WHERE id = ?", (self.member['id'],))
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"تمدید عضویت با خطا مواجه شد: {e}")
            return
        finally:
            try:
                conn.close()
            except:
                pass
        try:
            self.parent_widget.load_members()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بروزرسانی لیست اعضا با خطا مواجه شد: {e}")
