
from PyQt5 import QtCore, QtGui, QtWidgets
from .MembersWidget import MembersWidget
from .ManageWidget import ManageWidget
from .SettingWidget import SettingWidget
from jdatetime import datetime as jdatetime
import datetime
from .LoginWidget import LoginWidget
from .database import db

class Ui_Main(object):
    from .MusicPlayer import MusicPlayer
    def show_screensaver(self):
        from .ScreenSaver import ScreenSaverWidget
        if hasattr(self, 'screensaverWidget') and self.screensaverWidget is not None:
            self.verticalLayout_6.removeWidget(self.screensaverWidget)
            self.screensaverWidget.deleteLater()
        self.screensaverWidget = ScreenSaverWidget(self.screenWidget)
        self.verticalLayout_6.addWidget(self.screensaverWidget)
        self.show_only_in_screenWidget(self.screensaverWidget)
        self.screensaverWidget.parent().close_screensaver = self.close_screensaver

    def close_screensaver(self):
        if hasattr(self, 'screensaverWidget') and self.screensaverWidget is not None:
            self.verticalLayout_6.removeWidget(self.screensaverWidget)
            self.screensaverWidget.deleteLater()
            self.screensaverWidget = None
        self.show_dashboard()
    def show_manage_area(self):
        if not hasattr(self, 'manageWidget'):
            self.manageWidget = ManageWidget(self.screenWidget)
            self.verticalLayout_6.addWidget(self.manageWidget)
        self.show_only_in_screenWidget(self.manageWidget)

    def show_setting_area(self):
        if not hasattr(self, 'settingWidget'):
            self.settingWidget = SettingWidget(self.screenWidget)
            self.verticalLayout_6.addWidget(self.settingWidget)
        self.show_only_in_screenWidget(self.settingWidget)
    def handle_logout(self):
        # Stop music if playing
        if hasattr(self, 'musicPlayerWidget') and hasattr(self.musicPlayerWidget, 'stop_music'):
            self.musicPlayerWidget.stop_music()
        if hasattr(self, 'manageWidget') and hasattr(self.manageWidget, 'stop_music_on_logout'):
            self.manageWidget.stop_music_on_logout()
        mw = self.frame.parentWidget().window()
        mw.close()
        from .LoginWidget import LoginWidget
        login = LoginWidget()
        if login.exec_() == QtWidgets.QDialog.Accepted:
            user = getattr(login, 'user', None)
            Main = QtWidgets.QMainWindow()
            ui = Ui_Main()
            ui.setupUi(Main)
            if user and hasattr(ui, 'adminUsername') and 'full_name' in user:
                ui.adminUsername.setHtml(f'<p align="center">{user["full_name"]}</p>')
            Main.show()
            self._main_window = Main
        else:
            QtWidgets.QApplication.quit()
    def show_payment_area(self):
        try:
            total_members = db.get_total_members()
        except Exception:
            total_members = 0
        admin_name = None
        if hasattr(self, 'adminUsername') and hasattr(self.adminUsername, 'toPlainText'):
            admin_name = self.adminUsername.toPlainText().strip()
        if not hasattr(self, 'paymentWidget'):
            from .PaymentWidget import PaymentWidget
            self.paymentWidget = PaymentWidget(self.screenWidget, total_members=total_members, admin_name=admin_name)
            self.verticalLayout_6.addWidget(self.paymentWidget)
        else:
            self.paymentWidget.set_member_count(total_members)
            if hasattr(self.paymentWidget, 'set_admin_name'):
                self.paymentWidget.set_admin_name(admin_name)
        self.show_only_in_screenWidget(self.paymentWidget)
    def show_power_menu(self):
        if not hasattr(self, 'powerMenu'):
            self.powerMenu = QtWidgets.QFrame(self.centralwidget)
            self.powerMenu.setStyleSheet("background: white; border-radius: 18px; border: 2px solid #009966; font-family: 'Dubai Medium';")
            self.powerMenu.setGeometry(100, 100, 350, 300)
            layout = QtWidgets.QVBoxLayout(self.powerMenu)
            label = QtWidgets.QLabel("عملیات برنامه")
            label.setStyleSheet("font-size: 20pt; color: #009966; font-family: 'Dubai Medium';")
            layout.addWidget(label)
            btnMinimize = QtWidgets.QPushButton("کوچک کردن برنامه")
            btnMinimize.setStyleSheet("background: #888; color: white; font-size: 15pt; border-radius: 8px; font-family: 'Dubai Medium'; padding: 8px 16px;")
            btnCloseApp = QtWidgets.QPushButton("خروج از برنامه")
            btnCloseApp.setStyleSheet("background: #d32f2f; color: white; font-size: 15pt; border-radius: 8px; font-family: 'Dubai Medium'; padding: 8px 16px;")
            btnClose = QtWidgets.QPushButton("بستن منو")
            btnClose.setStyleSheet("background: #eee; color: #009966; font-size: 13pt; border-radius: 8px; font-family: 'Dubai Medium'; padding: 6px 12px;")
            layout.addWidget(btnMinimize)
            layout.addWidget(btnCloseApp)
            layout.addWidget(btnClose)
            btnMinimize.clicked.connect(self.minimize_app)
            btnCloseApp.clicked.connect(self.close_app)
            btnClose.clicked.connect(self.hide_power_menu)
        self.powerMenu.show()
        
    def hide_power_menu(self):
        if hasattr(self, 'powerMenu'):
            self.powerMenu.hide()


    def minimize_app(self):
        self.hide_power_menu()
        mw = self.frame.parentWidget()
        try:
            Main.showMinimized()
        except Exception:
            try:
                mw.window().showMinimized()
            except Exception:
                pass

    def close_app(self):
        self.hide_power_menu()
        dialog = QtWidgets.QDialog(self.frame)
        dialog.setWindowTitle("تایید خروج")
        dialog.setModal(True)
        dialog.setStyleSheet("background-color: #444; border-radius: 18px;")
        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("آیا مطمئن هستید که می‌خواهید از برنامه خارج شوید؟")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 22pt; font-family: 'Dubai Medium'; color: #fff; padding: 24px;")
        layout.addWidget(label)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_yes = QtWidgets.QPushButton("بله")
        btn_yes.setStyleSheet("font-size: 24pt; min-width: 140px; min-height: 60px; font-family: 'Dubai Medium'; background: #d32f2f; color: #fff; border-radius: 14px; padding: 18px 36px;")
        btn_no = QtWidgets.QPushButton("خیر")
        btn_no.setStyleSheet("font-size: 24pt; min-width: 140px; min-height: 60px; font-family: 'Dubai Medium'; background: #888; color: #fff; border-radius: 14px; padding: 18px 36px;")
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)
        layout.addLayout(btn_layout)
        btn_yes.clicked.connect(lambda: (dialog.accept(), QtWidgets.QApplication.quit()))
        btn_no.clicked.connect(dialog.reject)
        dialog.exec_()

    def menu_show(self):
        self.animate_menu_show()
    def menu_hide(self):
        self.animate_menu_hide()

    def animate_menu_show(self):
        self.frameMenu.setMaximumWidth(0)
        self.frameMenu.show()
        self.menu_anime = QtCore.QPropertyAnimation(self.frameMenu, b"maximumWidth")
        self.menu_anime.setDuration(350)
        self.menu_anime.setStartValue(0)
        self.menu_anime.setEndValue(275)
        self.menu_anime.start()

    def animate_menu_hide(self):
        self.menu_anime = QtCore.QPropertyAnimation(self.frameMenu, b"maximumWidth")
        self.menu_anime.setDuration(350)
        self.menu_anime.setStartValue(self.frameMenu.width())
        self.menu_anime.setEndValue(0)
        self.menu_anime.finished.connect(self.frameMenu.hide)
        self.menu_anime.start()

    def setupUi(self, Main, user=None):
        Main.setObjectName("Main")
        Main.showFullScreen()
        Main.setMinimumSize(QtCore.QSize(100, 100))
        Main.setStyleSheet("background-color: hsl(0, 0%, 90%);\n"
"background-image: url(:/bg/3312580.jpg);\n"
"background-repeat: no-repeat;\n"
"background-position: center;\n"
"")
        self.centralwidget = QtWidgets.QWidget(Main)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setStyleSheet("background: none;\nbackground-color: rgba(230, 230, 230, 40);\nborder-radius:25px;\n")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_6 = QtWidgets.QFrame(self.frame)
        self.frame_6.setMaximumSize(QtCore.QSize(16777215, 75))
        self.frame_6.setStyleSheet("background-color: hsl(0, 0%, 90%);\n"
"border-radius:25px;")
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnPower = QtWidgets.QPushButton(self.frame_6)
        self.btnPower.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"QPushButton:Hover{\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"}")
        self.btnPower.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/power.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnPower.setIcon(icon)
        self.btnPower.setIconSize(QtCore.QSize(50, 50))
        self.btnPower.setObjectName("btnPower")
        self.horizontalLayout_3.addWidget(self.btnPower)
        # Connect power button to show_power_menu
        try:
            self.btnPower.clicked.disconnect()
        except Exception:
            pass
        self.btnPower.clicked.connect(self.show_power_menu)
        self.line_3 = QtWidgets.QFrame(self.frame_6)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_3.addWidget(self.line_3)
        self.textCalendar = QtWidgets.QTextBrowser(self.frame_6)
        self.textCalendar.setMaximumSize(QtCore.QSize(16777215, 65))
        self.textCalendar.setStyleSheet("background-color: hsl(0, 0%, 100%);\n"
"font: 16pt \"B Yekan\";")
        self.textCalendar.setObjectName("textCalendar")
        self.horizontalLayout_3.addWidget(self.textCalendar)
        self.textMenu = QtWidgets.QTextBrowser(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textMenu.sizePolicy().hasHeightForWidth())
        self.textMenu.setSizePolicy(sizePolicy)
        self.textMenu.setMaximumSize(QtCore.QSize(16777215, 65))
        self.textMenu.setStyleSheet("background-color: hsl(0, 0%, 100%);\n"
"font: 57 16pt \"Dubai Medium\";")
        self.textMenu.setObjectName("textMenu")
        self.horizontalLayout_3.addWidget(self.textMenu)
        self.textTime = QtWidgets.QTextBrowser(self.frame_6)
        self.textTime.setMaximumSize(QtCore.QSize(16777215, 65))
        self.textTime.setStyleSheet("background-color: hsl(0, 0%, 100%);\n"
"font: 16pt \"B Yekan\";")
        self.textTime.setObjectName("textTime")
        self.horizontalLayout_3.addWidget(self.textTime)
        self.line_4 = QtWidgets.QFrame(self.frame_6)
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_3.addWidget(self.line_4)
        self.btnMenu = QtWidgets.QPushButton(self.frame_6)
        self.btnMenu.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"    border-radius:none;\n"
"}\n"
"QPushButton:Hover{\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"}")
        self.btnMenu.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/menu.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnMenu.setIcon(icon1)
        self.btnMenu.setIconSize(QtCore.QSize(50, 50))
        self.btnMenu.setObjectName("btnMenu")
        # Add a flag to track menu state
        self.menu_is_open = False

        # Disconnect previous connections to avoid duplicate triggers
        try:
            self.btnMenu.clicked.disconnect()
        except Exception:
            pass

        def toggle_menu():
            if self.menu_is_open:
                self.menu_hide()
                self.menu_is_open = False
            else:
                self.menu_show()
                self.menu_is_open = True

        self.btnMenu.clicked.connect(toggle_menu)
        
        self.horizontalLayout_3.addWidget(self.btnMenu)
        self.verticalLayout_3.addWidget(self.frame_6)
        self.screenWidget = QtWidgets.QWidget(self.frame)
        self.screenWidget.setStyleSheet("background-color: rgba(230, 230, 230, 20);\n"
"")
        self.screenWidget.setObjectName("screenWidget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.screenWidget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.Dashboard = QtWidgets.QFrame(self.screenWidget)
        self.Dashboard.setStyleSheet("background-color: rgba(230, 230, 230, 0);\n"
"")
        self.Dashboard.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Dashboard.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Dashboard.setObjectName("Dashboard")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.Dashboard)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.widget_3 = QtWidgets.QWidget(self.Dashboard)
        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 150))
        self.widget_3.setStyleSheet("background-color: rgba(230, 230, 230, 0);\n"
"")
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gymStat = QtWidgets.QWidget(self.widget_3)
        self.gymStat.setStyleSheet("QWidget{\n"
"background-color: hsl(0, 0%, 100%);\n"
"font: 16pt \"B Yekan\";\n"
"border-radius:25px;\n"
"}\n"
"QWidget:Hover{\n"
"background-color: hsl(0, 0%, 95%);\n"
"}\n"
"\n"
"")
        self.gymStat.setObjectName("gymStat")
        self.horizontalLayout_4.addWidget(self.gymStat)
        self.gymStat_2 = QtWidgets.QWidget(self.widget_3)
        self.gymStat_2.setStyleSheet("QWidget{\n"
"background-color: hsl(0, 0%, 100%);\n"
"font: 16pt \"B Yekan\";\n"
"border-radius:25px;\n"
"}\n"
"QWidget:Hover{\n"
"background-color: hsl(0, 0%, 95%);\n"
"}\n"
"\n"
"")
        self.gymStat_2.setObjectName("gymStat_2")
        self.horizontalLayout_4.addWidget(self.gymStat_2)
        self.gymStat_3 = QtWidgets.QWidget(self.widget_3)
        self.gymStat_3.setStyleSheet("QWidget{\n"
"background-color: hsl(0, 0%, 100%);\n"
"font: 16pt \"B Yekan\";\n"
"border-radius:25px;\n"
"}\n"
"QWidget:Hover{\n"
"background-color: hsl(0, 0%, 95%);\n"
"}\n"
"\n"
"")
        self.gymStat_3.setObjectName("gymStat_3")
        self.horizontalLayout_4.addWidget(self.gymStat_3)
        self.gymStat_4 = QtWidgets.QWidget(self.widget_3)
        self.gymStat_4.setStyleSheet("QWidget{\n"
"background-color: hsl(0, 0%, 100%);\n"
"font: 16pt \"B Yekan\";\n"
"border-radius:25px;\n"
"}\n"
"QWidget:Hover{\n"
"background-color: hsl(0, 0%, 95%);\n"
"}\n"
"\n"
"")
        self.gymStat_4.setObjectName("gymStat_4")
        self.horizontalLayout_4.addWidget(self.gymStat_4)
        self.verticalLayout_7.addWidget(self.widget_3)
        self.widget_2 = QtWidgets.QWidget(self.Dashboard)
        self.widget_2.setStyleSheet("background-color: rgba(230, 230, 230, 0);\n"
"")
        self.widget_2.setObjectName("widget_2")
        self.hBox_recent = QtWidgets.QHBoxLayout(self.widget_2)
        self.hBox_recent.setObjectName("hBox_recent")

        # Recently Joined Widget
        from .RecentlyJoinedWidget import RecentlyJoinedWidget
        self.RecentlyJoined = RecentlyJoinedWidget(self.widget_2)
        self.RecentlyJoined.setObjectName("RecentlyJoined")
        if hasattr(self.RecentlyJoined, 'set_display_fields'):
            self.RecentlyJoined.set_display_fields(['name', 'surname', 'id'])
        if hasattr(self.RecentlyJoined, 'set_centered'):
            self.RecentlyJoined.set_centered(True)
        self.hBox_recent.addWidget(self.RecentlyJoined)

        # Expiring Members Widget
        from .ExpiringMembersWidget import ExpiringMembersWidget
        self.ExpiringMembers = ExpiringMembersWidget(self.widget_2)
        self.ExpiringMembers.setObjectName("ExpiringMembers")
        self.hBox_recent.addWidget(self.ExpiringMembers)

        # Connect screensaver button
        if hasattr(self.RecentlyJoined, 'screensaver_btn'):
            self.RecentlyJoined.screensaver_btn.clicked.connect(self.show_screensaver)

        self.verticalLayout_7.addWidget(self.widget_2)
        self.verticalLayout_6.addWidget(self.Dashboard)

        # Add MusicPlayer widget to the bottom of the dashboard area
        self.musicPlayerWidget = self.MusicPlayer(self.Dashboard)
        self.verticalLayout_7.addWidget(self.musicPlayerWidget)
        self.verticalLayout_3.addWidget(self.screenWidget)
        self.horizontalLayout.addWidget(self.frame)
        self.frameMenu = QtWidgets.QFrame(self.centralwidget)
        self.menu_anime = QtCore.QPropertyAnimation(self.frameMenu, b"maximumWidth")
        self.menu_anime.setDuration(350)
        self.menu_anime.setStartValue(0)
        self.menu_anime.setEndValue(275)  # Width of the menu
        self.frameMenu.setMaximumSize(QtCore.QSize(275, 16777215))
        self.frameMenu.setStyleSheet("background: none;\n"
"background-color: hsl(219, 51%, 32%);\n"
"border:none;"
"")
        self.frameMenu.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMenu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMenu.setObjectName("frameMenu")
        self.menu_hide()
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameMenu)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Logo = QtWidgets.QFrame(self.frameMenu)
        self.Logo.setMaximumSize(QtCore.QSize(16777215, 150))
        self.Logo.setStyleSheet("image: url(:/pp/logo.png);")
        self.Logo.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Logo.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Logo.setObjectName("Logo")
        self.verticalLayout.addWidget(self.Logo)
        self.frame_5 = QtWidgets.QFrame(self.frameMenu)
        self.frame_5.setStyleSheet("")
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.line_2 = QtWidgets.QFrame(self.frame_5)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_4.addWidget(self.line_2)
        self.btnDashboard = QtWidgets.QPushButton(self.frame_5)
        self.btnDashboard.setMinimumSize(QtCore.QSize(0, 75))
        self.btnDashboard.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btnDashboard.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"QPushButton:Hover{\n"
"    background-color: hsl(219, 62%, 32%);\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"    border-bottom:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    background-color: hsl(219, 72%, 32%);\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"    border-top:none;\n"
"}")
        self.btnDashboard.setObjectName("btnDashboard")
        self.verticalLayout_4.addWidget(self.btnDashboard)
        self.btnPayment = QtWidgets.QPushButton(self.frame_5)
        self.btnPayment.setMinimumSize(QtCore.QSize(0, 75))
        self.btnPayment.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btnPayment.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"QPushButton:Hover{\n"
"    background-color: hsl(219, 62%, 32%);\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"    border-bottom:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    background-color: hsl(219, 72%, 32%);\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"    border-top:none;\n"
"}")
        self.btnPayment.setObjectName("btnPayment")
        self.verticalLayout_4.addWidget(self.btnPayment)
        # Connect payment button to show_payment_area
        try:
            self.btnPayment.clicked.disconnect()
        except Exception:
            pass
        self.btnPayment.clicked.connect(self.show_payment_area)
        self.btnMembers = QtWidgets.QPushButton(self.frame_5)
        self.btnMembers.setMinimumSize(QtCore.QSize(0, 75))
        self.btnMembers.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btnMembers.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"QPushButton:Hover{\n"
"    background-color: hsl(219, 62%, 32%);\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"    border-bottom:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    background-color: hsl(219, 72%, 32%);\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"    border-top:none;\n"
"}")
        self.btnMembers.setObjectName("btnMembers")
        self.verticalLayout_4.addWidget(self.btnMembers)
        self.btnManage = QtWidgets.QPushButton(self.frame_5)
        self.btnManage.setMinimumSize(QtCore.QSize(0, 75))
        self.btnManage.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btnManage.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"QPushButton:Hover{\n"
"    background-color: hsl(219, 62%, 32%);\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"    border-bottom:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    background-color: hsl(219, 72%, 32%);\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"    border-top:none;\n"
"}")
        self.btnManage.setObjectName("btnManage")
        self.verticalLayout_4.addWidget(self.btnManage)
        self.btnSettings = QtWidgets.QPushButton(self.frame_5)
        self.btnSettings.setMinimumSize(QtCore.QSize(0, 75))
        self.btnSettings.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btnSettings.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"QPushButton:Hover{\n"
"    background-color: hsl(219, 62%, 32%);\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"    border-bottom:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    background-color: hsl(219, 72%, 32%);\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"    border-top:none;\n"
"}")
        self.btnSettings.setObjectName("btnSettings")
        self.verticalLayout_4.addWidget(self.btnSettings)
        self.line = QtWidgets.QFrame(self.frame_5)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_4.addWidget(self.line)
        self.verticalLayout.addWidget(self.frame_5)
        self.frame_4 = QtWidgets.QFrame(self.frameMenu)
        self.frame_4.setMaximumSize(QtCore.QSize(16777215, 200))
        self.frame_4.setStyleSheet("")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.adminProfile = QtWidgets.QLabel(self.frame_4)
        self.adminProfile.setMinimumSize(QtCore.QSize(100, 100))
        self.adminProfile.setStyleSheet("image: url(:/pp/user.png);")
        self.adminProfile.setText("")
        self.adminProfile.setObjectName("adminProfile")
        self.verticalLayout_2.addWidget(self.adminProfile)
        self.adminUsername = QtWidgets.QTextBrowser(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.adminUsername.sizePolicy().hasHeightForWidth())
        self.adminUsername.setSizePolicy(sizePolicy)
        self.adminUsername.setMaximumSize(QtCore.QSize(16777215, 60))
        self.adminUsername.setStyleSheet("border:none;\n"
"color:white;\n"
"font: 16pt \"Dubai Medium\";\n"
"border:2px solid white;\n"
"border-radius:25px;")
        self.adminUsername.setObjectName("adminUsername")
        self.verticalLayout_2.addWidget(self.adminUsername)
        # Set admin full name if user is provided
        if user and 'full_name' in user:
            self.adminUsername.setHtml(f'<p align="center">{user["full_name"]}</p>')
        self.verticalLayout.addWidget(self.frame_4)
        self.btnLogOut = QtWidgets.QPushButton(self.frameMenu)
        self.btnLogOut.setMinimumSize(QtCore.QSize(0, 50))
        self.btnLogOut.setMaximumSize(QtCore.QSize(16777215, 75))
        self.btnLogOut.setStyleSheet("QPushButton{\n"
"    font: 57 18pt \"Dubai Medium\";\n"
"    color: rgb(255, 255, 255);\n"
"\n"
"}\n"
"QPushButton:Hover{\n"
"    background-color: hsl(219, 62%, 32%);\n"
"    border:2px solid white;\n"
"    border-top:none;\n"
"    border-left:none;\n"
"}\n"
"QPushButton:Pressed{\n"
"    background-color: hsl(219, 72%, 32%);\n"
"    border:2px solid white;\n"
"    border-bottom:none;\n"
"    border-right:none;\n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/bg/out.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnLogOut.setIcon(icon2)
        self.btnLogOut.setIconSize(QtCore.QSize(50, 50))
        self.btnLogOut.setObjectName("btnLogOut")
        self.verticalLayout.addWidget(self.btnLogOut)
        try:
            self.btnLogOut.clicked.disconnect()
        except Exception:
            pass
        self.btnLogOut.clicked.connect(self.handle_logout)
        self.horizontalLayout.addWidget(self.frameMenu)
        Main.setCentralWidget(self.centralwidget)
        self.centralwidget.show()

        self.retranslateUi(Main)
        QtCore.QMetaObject.connectSlotsByName(Main)

        # Set admin full name in adminUsername textBrowser if available (override default)
        if user and 'full_name' in user:
            self.adminUsername.setHtml(f'<p align="center">{user["full_name"]}</p>')

        # Get admin name if available
        admin_name = None
        if hasattr(self, 'adminUsername') and hasattr(self.adminUsername, 'toPlainText'):
            admin_name = self.adminUsername.toPlainText().strip()
            
        self.membersWidget = MembersWidget(self.screenWidget, main_window=self, admin_name=admin_name)
        self.membersWidget.hide()
        self.btnMembers.clicked.connect(self.show_members_area)

        self.btnManage.clicked.connect(self.show_manage_area)
        self.btnSettings.clicked.connect(self.show_setting_area)

        self.btnDashboard.clicked.connect(self.show_dashboard)
        # Set current_shift based on current time
        now = datetime.datetime.now()
        hour = now.hour
        if 9 <= hour < 14:
            self.current_shift = 'women'
        elif 14 <= hour < 24:
            self.current_shift = 'men'
        else:
            self.current_shift = 'men'  # Default to men if outside defined hours
        # Show dashboard by default
        self.show_dashboard()

    def show_only_in_screenWidget(self, widget):
        # Hide all widgets in screenWidget's layout
        for i in range(self.verticalLayout_6.count()):
            w = self.verticalLayout_6.itemAt(i).widget()
            if w:
                w.hide()
        # Show the requested widget
        widget.show()
        if self.verticalLayout_6.indexOf(widget) == -1:
            self.verticalLayout_6.addWidget(widget)

    def show_members_area(self):
        self.show_only_in_screenWidget(self.membersWidget)

    def show_dashboard(self):
        self.show_only_in_screenWidget(self.Dashboard)
        self.update_dashboard_stats()

    def toggle_shift(self):
        self.current_shift = 'women' if self.current_shift == 'men' else 'men'
        self.update_dashboard_stats()

    def update_dashboard_stats(self):
        try:
            stats = db.get_dashboard_stats(self.current_shift)
            total_active = stats['total_active']
            shift_count = stats['shift_count']
            expiring = stats['expiring']
            recent = stats['recent']
        except Exception as e:
            print(f"Dashboard DB error: {e}")
            total_active = shift_count = expiring = recent = 0
        # Display stats
        for stat_widget in [self.gymStat, self.gymStat_2, self.gymStat_3, self.gymStat_4]:
            layout = stat_widget.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                stat_widget.setLayout(QtWidgets.QVBoxLayout())
        self.gymStat.layout().addWidget(QtWidgets.QLabel(f"اعضای فعال: {total_active}"))
        self.gymStat_2.layout().addWidget(QtWidgets.QLabel(f"شیفت جاری: {'آقایان' if self.current_shift == 'men' else 'بانوان'}"))
        shiftToggle = QtWidgets.QPushButton('تغییر شیفت', self.gymStat_2)
        shiftToggle.setStyleSheet("font-size: 16pt; font-family: 'Dubai Medium'; background: #3c096c; color: #fff; border-radius: 12px; padding: 8px 24px;")
        shiftToggle.setGeometry(10, 10, 140, 40)
        shiftToggle.clicked.connect(self.toggle_shift)
        self.gymStat_2.layout().addWidget(shiftToggle)
        expiring_count = 0
        if hasattr(self, 'ExpiringMembers') and hasattr(self.ExpiringMembers, 'get_expiring_count'):
            expiring_count = self.ExpiringMembers.get_expiring_count()
        self.gymStat_3.layout().addWidget(QtWidgets.QLabel(f"عضویت‌های در حال انقضا: {expiring_count}"))
        self.gymStat_4.layout().addWidget(QtWidgets.QLabel(f"ورودهای اخیر: {recent}"))

    def retranslateUi(self, Main):
        _translate = QtCore.QCoreApplication.translate
        Main.setWindowTitle(_translate("Main", "MainWindow"))
        self.textCalendar.setHtml(_translate("Main", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'B Yekan\'; font-size:16pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1404/4/20</p></body></html>"))
        self.textMenu.setHtml(_translate("Main", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Dubai Medium\'; font-size:16pt; font-weight:56; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">باشگاه بدنسازی آراز</p></body></html>"))
        self.textTime.setHtml(_translate("Main", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'B Yekan\'; font-size:16pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">11:11:11</p></body></html>"))
        self.RecentlyJoined.setStyleSheet(_translate("Main", "QWidget{\n"
"background-color: hsl(0, 0%, 100%);\n"
"font: 16pt \"B Yekan\";\n"
"border-radius:25px;\n"
"}\n"
"QWidget:Hover{\n"
"background-color: hsl(0, 0%, 95%);\n"
"}\n"
"\n"
""))
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_clock_and_calendar)
        self.timer.start(1000)
        self.update_clock_and_calendar()
        
        self.btnDashboard.setText (_translate("Main", "داشبورد"))
        self.btnPayment.setText   (_translate("Main", "امور مالی"))
        self.btnMembers.setText   (_translate("Main", "مدیریت ورزشکاران"))
        self.btnManage.setText    (_translate("Main", "مدیریت باشگاه"))
        self.btnSettings.setText  (_translate("Main", "تنظیمات"))
        self.adminUsername.setHtml(_translate("Main", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Dubai Medium\'; font-size:16pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">مهدی پورغفار</p></body></html>"))
        self.btnLogOut.setText(_translate("Main", "خروج کاربر"))
        
        
    def update_clock_and_calendar(self):
        try:
            now = datetime.datetime.now()
            self.textTime.setHtml(f'<div align="center">{now.strftime("%H:%M:%S")}</div>')
            jnow = jdatetime.now()
            jalali_date = jnow.strftime("%Y/%m/%d")
            self.textCalendar.setHtml(f'<div align="center">{jalali_date}</div>')
            hour = now.hour
            prev_shift = getattr(self, 'current_shift', None)
            if 9 <= hour < 14:
                self.current_shift = 'women'
            elif 14 <= hour < 24:
                self.current_shift = 'men'
            else:
                self.current_shift = 'men'
            if prev_shift != self.current_shift:
                self.update_dashboard_stats()
        except Exception as e:
            # Fallback: show error or blank
            self.textCalendar.setHtml('<div align="center">خطا در تاریخ</div>')
            self.textTime.setHtml('<div align="center">--:--:--</div>')
        


from . import MainPack_rc


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    login = LoginWidget()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        user = getattr(login, 'user', None)
        Main = QtWidgets.QMainWindow()
        ui = Ui_Main()
        ui.setupUi(Main, user=user)
        Main.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

# from PyQt5.QtWidgets import QApplication
# if __name__ == "__main__":
#     import sys
#     from LoginWidget import LoginWidget
#     app = QtWidgets.QApplication(sys.argv)
#     # Show login dialog
#     login = LoginWidget()
#     if login.exec_() == QtWidgets.QDialog.Accepted:
#         Main = QtWidgets.QMainWindow()
#         ui = Ui_Main()
#         ui.setupUi(Main)
#         Main.show()
#         sys.exit(app.exec_())
#     else:
#         sys.exit(0)

#Direct login for testing purposes
# if __name__ == '__main__':
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     app.setStyle('Fusion')
#     login = LoginWidget()
#     user = getattr(login, 'user', None)
#     Main = QtWidgets.QMainWindow()
#     ui = Ui_Main()
#     ui.setupUi(Main)
#     # Set admin full name in adminUsername textBrowser if available
#     Main.show()
#     sys.exit(app.exec_())
# else:
#     sys.exit(0)