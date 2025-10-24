from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
import sqlite3
import os
from datetime import datetime
import shutil

class EquipmentCard(QtWidgets.QWidget):
    def __init__(self, equipment, parent_widget, parent=None):
        super().__init__(parent)
        self.equipment = equipment
        self.parent_widget = parent_widget
        self.form_visible = False
        self.init_ui()

    def init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        # Equipment info card
        self.card_content = QtWidgets.QWidget()
        card_layout = QtWidgets.QVBoxLayout(self.card_content)
        
        # Format purchase date
        purchase_date = self.equipment['purchase_date'] if 'purchase_date' in self.equipment.keys() else ''
        if purchase_date:
            try:
                dt = datetime.fromisoformat(purchase_date.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%Y/%m/%d')
            except:
                formatted_date = purchase_date
        else:
            formatted_date = '-'
        
        # Equipment name
        equipment_name = self.equipment['name'] if 'name' in self.equipment.keys() else 'نامشخص'
        
        # Equipment status
        status = self.equipment['status'] if 'status' in self.equipment.keys() else 'سالم و ایمن'
        status_color = {
            'سالم و ایمن': '#009966',
            'نیازمند تعمیر': '#d32f2f',
            'خراب': '#d32f2f',
            'در حال تعمیر': '#ff9800'
        }.get(status, '#666')
        
        info = f"""
        <div style='color:black; font-size:18pt; font-family: "B Yekan"; font-weight:bold;'>{equipment_name}</div>
        <div style='color:black; font-size:12pt; font-family: "B Yekan";'>تاریخ خرید: {formatted_date}</div>
        <div style='color:{status_color}; font-size:12pt; font-family: "B Yekan"; font-weight:bold;'>وضعیت: {status}</div>
        <div style='color:#666; font-size:11pt; font-family: "B Yekan";'>توضیحات: {self.equipment['description'] if 'description' in self.equipment.keys() else '-'}</div>
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
        
        # Create edit form
        self.edit_form = QtWidgets.QWidget()
        edit_layout = QtWidgets.QVBoxLayout(self.edit_form)
        
        # Edit fields
        form_layout = QtWidgets.QFormLayout()
        
        self.edit_name = QtWidgets.QLineEdit(self.equipment['name'] if 'name' in self.equipment.keys() else '')
        self.edit_purchase_date = QtWidgets.QLineEdit(self.equipment['purchase_date'] if 'purchase_date' in self.equipment.keys() else '')
        self.edit_description = QtWidgets.QLineEdit(self.equipment['description'] if 'description' in self.equipment.keys() else '')
        self.edit_status = QtWidgets.QComboBox()
        self.edit_status.addItems(['سالم و ایمن', 'نیازمند تعمیر', 'خراب', 'در حال تعمیر'])
        self.edit_status.setCurrentText(self.equipment['status'] if 'status' in self.equipment.keys() else 'سالم و ایمن')
        
        for inp in [self.edit_name, self.edit_purchase_date, self.edit_description]:
            inp.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'B Yekan';")
        
        self.edit_status.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'B Yekan';")
        
        form_layout.addRow("نام تجهیز:", self.edit_name)
        form_layout.addRow("تاریخ خرید:", self.edit_purchase_date)
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
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.card_content)
        self.main_layout.addWidget(self.edit_form)
        
        self.setStyleSheet("QWidget { background: rgba(255,255,255,100); border-radius: 18px; padding: 18px; font-family: 'B Yekan'; }")
        
        # Connect buttons
        edit_btn.clicked.connect(self.show_edit_form)
        delete_btn.clicked.connect(self.delete_equipment)
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
            name = self.edit_name.text().strip()
            purchase_date = self.edit_purchase_date.text().strip()
            description = self.edit_description.text().strip()
            status = self.edit_status.currentText()
            
            if not name:
                QtWidgets.QMessageBox.warning(self, "خطا", "لطفا نام تجهیز را وارد کنید.")
                return
            
            # Update equipment
            from .database import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE equipment 
                    SET name = ?, purchase_date = ?, description = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (name, purchase_date, description, status, self.equipment['id']))
                conn.commit()

            self.hide_edit_form()
            self.parent_widget.load_equipment()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"ذخیره تغییرات با خطا مواجه شد: {e}")

    def delete_equipment(self):
        reply = QtWidgets.QMessageBox.question(
            self,
            "تایید حذف",
            "آیا از حذف این تجهیز اطمینان دارید؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                from .database import db
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM equipment WHERE id = ?", (self.equipment['id'],))
                    conn.commit()
                
                self.parent_widget.load_equipment()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "خطا", f"حذف تجهیز با خطا مواجه شد: {e}")


class ManageWidget(QtWidgets.QWidget):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.form_visible = False
        self.init_ui()
        self.load_equipment()



    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        # Top bar
        top_bar = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("<div style='color:white; font-family: \"Dubai Medium\"; font-size: 32pt; font-weight: bold;'>مدیریت باشگاه</div><div style='color:white; font-family: \"Dubai Medium\"; font-size: 18pt;'>تجهیزات</div>")
        title.setTextFormat(QtCore.Qt.RichText)
        top_bar.addWidget(title)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        # Only equipment section
        self.equipment_widget = self.create_equipment_section()
        main_layout.addWidget(self.equipment_widget)

    def create_equipment_section(self):
        equipment_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(equipment_widget)
        
        # Add equipment button
        add_btn_layout = QtWidgets.QHBoxLayout()
        add_equipment_btn = QtWidgets.QPushButton("+ افزودن تجهیز جدید")
        add_equipment_btn.setFixedHeight(50)
        add_equipment_btn.setStyleSheet("background: #009966; color: #fff; font-weight: bold; border-radius: 8px; padding: 0 16px; font-size: 13pt; font-family: 'Dubai Medium';")
        add_btn_layout.addWidget(add_equipment_btn)
        add_btn_layout.addStretch()
        layout.addLayout(add_btn_layout)
        
        # Add Equipment Form (hidden by default)
        self.add_equipment_form = QtWidgets.QFrame()
        self.add_equipment_form.setStyleSheet("background: rgba(255,255,255,0.95); border-radius: 18px; padding: 18px; font-family: 'Dubai Medium';")
        self.add_equipment_form.setMaximumHeight(0)
        
        form_layout = QtWidgets.QFormLayout(self.add_equipment_form)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setFormAlignment(QtCore.Qt.AlignRight)
        
        # Form fields
        self.input_equipment_name = QtWidgets.QLineEdit()
        self.input_purchase_date = QtWidgets.QLineEdit()
        self.input_equipment_description = QtWidgets.QLineEdit()
        self.input_equipment_status = QtWidgets.QComboBox()
        self.input_equipment_status.addItems(['سالم و ایمن', 'نیازمند تعمیر', 'خراب', 'در حال تعمیر'])
        
        self.input_equipment_name.setPlaceholderText("نام تجهیز")
        self.input_purchase_date.setPlaceholderText("تاریخ خرید (مثال: 1403/05/15)")
        self.input_equipment_description.setPlaceholderText("توضیحات")
        
        for inp in [self.input_equipment_name, self.input_purchase_date, self.input_equipment_description, self.input_equipment_status]:
            inp.setStyleSheet("font-size: 15pt; padding: 8px 16px; border-radius: 8px; font-family: 'Dubai Medium'; min-width: 900px; width: 75%;")
        
        label_style = "font-size: 15pt; font-family: 'Dubai Medium'; color: #444; padding: 8px; border-radius: 8px; background: #f7f7f7; min-width: 100px; text-align: right;"
        
        form_layout.addRow(self.input_equipment_name, QtWidgets.QLabel("نام تجهیز:"))
        form_layout.itemAt(0, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        form_layout.addRow(self.input_purchase_date, QtWidgets.QLabel("تاریخ خرید:"))
        form_layout.itemAt(1, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        form_layout.addRow(self.input_equipment_description, QtWidgets.QLabel("توضیحات:"))
        form_layout.itemAt(2, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        form_layout.addRow(self.input_equipment_status, QtWidgets.QLabel("وضعیت:"))
        form_layout.itemAt(3, QtWidgets.QFormLayout.FieldRole).widget().setStyleSheet(label_style)
        
        self.submit_equipment_btn = QtWidgets.QPushButton("ثبت تجهیز")
        self.submit_equipment_btn.setStyleSheet("background: #009966; color: #fff; font-weight: bold; border-radius: 8px; padding: 12px 24px; font-size: 16pt; font-family: 'Dubai Medium';")
        form_layout.addRow(self.submit_equipment_btn)
        
        layout.addWidget(self.add_equipment_form)
        
        # Animation for slide down
        self.equipment_form_anim = QtCore.QPropertyAnimation(self.add_equipment_form, b"maximumHeight")
        self.equipment_form_anim.setDuration(350)
        self.equipment_form_anim.setStartValue(0)
        self.equipment_form_anim.setEndValue(350)
        
        # Search section
        search_layout = QtWidgets.QHBoxLayout()
        
        self.equipment_search_edit = QtWidgets.QLineEdit()
        self.equipment_search_edit.setPlaceholderText("جستجو بر اساس نام تجهیز...")
        self.equipment_search_edit.setStyleSheet("color: white; background: rgba(255,255,255,0.08); border-radius: 8px; font-size: 15pt; padding: 8px 16px; font-family: 'Dubai Medium';")
        search_layout.addWidget(self.equipment_search_edit)
        
        self.equipment_filter_combo = QtWidgets.QComboBox()
        self.equipment_filter_combo.addItems(["همه تجهیزات", "سالم و ایمن", "نیازمند تعمیر", "خراب", "در حال تعمیر"])
        self.equipment_filter_combo.setStyleSheet("color: white; background: rgba(255,255,255,45); border-radius: 8px; font-size: 15pt; font-family: 'Dubai Medium';")
        search_layout.addWidget(self.equipment_filter_combo)
        
        layout.addLayout(search_layout)
        
        # Scroll area for equipment cards
        self.equipment_scroll = QtWidgets.QScrollArea()
        self.equipment_scroll.setWidgetResizable(True)
        self.equipment_cards_container = QtWidgets.QWidget()
        self.equipment_cards_layout = QtWidgets.QGridLayout(self.equipment_cards_container)
        self.equipment_cards_layout.setSpacing(20)
        self.equipment_scroll.setWidget(self.equipment_cards_container)
        layout.addWidget(self.equipment_scroll)
        
        # Connect buttons and filters
        add_equipment_btn.clicked.connect(self.toggle_equipment_form)
        self.submit_equipment_btn.clicked.connect(self.submit_equipment)
        self.equipment_search_edit.textChanged.connect(self.filter_equipment)
        self.equipment_filter_combo.currentTextChanged.connect(self.filter_equipment)
        
        return equipment_widget




    def toggle_equipment_form(self):
        if self.form_visible:
            self.equipment_form_anim.setDirection(QtCore.QAbstractAnimation.Backward)
            self.equipment_form_anim.start()
            self.form_visible = False
        else:
            self.equipment_form_anim.setDirection(QtCore.QAbstractAnimation.Forward)
            self.equipment_form_anim.start()
            self.form_visible = True

    def submit_equipment(self):
        name = self.input_equipment_name.text().strip()
        purchase_date = self.input_purchase_date.text().strip()
        description = self.input_equipment_description.text().strip()
        status = self.input_equipment_status.currentText()
        
        if not name:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("خطا")
            msg.setText("لطفا نام تجهیز را وارد کنید")
            msg.setStyleSheet("""
                QMessageBox {
                    font-family: 'B Yekan';
                    font-size: 14pt;
                }
                QMessageBox QPushButton {
                    font-family: 'B Yekan';
                    font-size: 12pt;
                    min-width: 100px;
                    padding: 6px;
                    background: #d32f2f;
                    color: white;
                    border-radius: 5px;
                }
            """)
            msg.exec_()
            return
        
        try:
            from .database import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO equipment (name, purchase_date, description, status)
                    VALUES (?, ?, ?, ?)
                """, (name, purchase_date, description, status))
                conn.commit()
            
            # Clear form
            self.input_equipment_name.clear()
            self.input_purchase_date.clear()
            self.input_equipment_description.clear()
            self.input_equipment_status.setCurrentIndex(0)
            
            self.toggle_equipment_form()
            self.load_equipment()
            
            success_msg = QtWidgets.QMessageBox()
            success_msg.setIcon(QtWidgets.QMessageBox.Information)
            success_msg.setWindowTitle("موفقیت")
            success_msg.setText("تجهیز جدید با موفقیت ثبت شد")
            success_msg.setInformativeText("تجهیز مورد نظر به لیست تجهیزات اضافه شد.")
            success_msg.setStyleSheet("""
                QMessageBox {
                    font-family: 'B Yekan';
                    font-size: 14pt;
                }
                QMessageBox QPushButton {
                    font-family: 'B Yekan';
                    font-size: 12pt;
                    min-width: 100px;
                    padding: 6px;
                    background: #009966;
                    color: white;
                    border-radius: 5px;
                }
            """)
            success_msg.exec_()
            
        except Exception as e:
            error_msg = QtWidgets.QMessageBox()
            error_msg.setIcon(QtWidgets.QMessageBox.Critical)
            error_msg.setWindowTitle("خطا")
            error_msg.setText("خطا در ثبت تجهیز")
            error_msg.setInformativeText(f"ثبت تجهیز با خطای زیر مواجه شد:\n{str(e)}")
            error_msg.setStyleSheet("""
                QMessageBox {
                    font-family: 'B Yekan';
                    font-size: 14pt;
                }
                QMessageBox QPushButton {
                    font-family: 'B Yekan';
                    font-size: 12pt;
                    min-width: 100px;
                    padding: 6px;
                    background: #d32f2f;
                    color: white;
                    border-radius: 5px;
                }
            """)
            error_msg.exec_()

    def load_equipment(self, filter_text=None, status_filter=None):
        try:
            from .database import db
            conn = db.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM equipment WHERE 1=1"
            params = []
            
            if filter_text:
                query += " AND name LIKE ?"
                params.append(f"%{filter_text}%")
            
            if status_filter and status_filter != "همه تجهیزات":
                query += " AND status = ?"
                params.append(status_filter)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            equipment_list = cursor.fetchall()
            
            conn.close()
            
            # Clear old cards
            for i in reversed(range(self.equipment_cards_layout.count())):
                widget = self.equipment_cards_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Add equipment cards
            for idx, equipment in enumerate(equipment_list):
                card = EquipmentCard(equipment, parent_widget=self, parent=self)
                row = idx // 3
                col = idx % 3
                self.equipment_cards_layout.addWidget(card, row, col)
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"بارگذاری تجهیزات با خطا مواجه شد: {e}")

    def filter_equipment(self):
        filter_text = self.equipment_search_edit.text()
        status_filter = self.equipment_filter_combo.currentText()
        self.load_equipment(filter_text, status_filter)


