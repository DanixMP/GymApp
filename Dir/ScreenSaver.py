from PyQt5 import QtCore, QtGui, QtWidgets
import datetime

class ScreenSaverWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #111;")
        self.setObjectName("ScreenSaverWidget")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        self.clockWidget = None
        self.imageWidget = None
        self.mode = None
        self.available_modes = ['clock', 'image']
        self.init_ui()

    def init_ui(self):
        btn_layout = QtWidgets.QHBoxLayout()
        self.btnClock = QtWidgets.QPushButton("ساعت")
        self.btnClock.setStyleSheet("font-size: 22pt; background: #222; color: #fff; border-radius: 12px; padding: 16px 32px;")
        self.btnImage = QtWidgets.QPushButton("تصویر")
        self.btnImage.setStyleSheet("font-size: 22pt; background: #222; color: #fff; border-radius: 12px; padding: 16px 32px;")
        btn_layout.addWidget(self.btnClock)
        btn_layout.addWidget(self.btnImage)
        self.layout.addLayout(btn_layout)
        self.btnClock.clicked.connect(self.show_clock)
        self.btnImage.clicked.connect(self.show_image)

    def show_clock(self):
        self.clear_mode()
        self.mode = 'clock'
        self.clockWidget = QtWidgets.QLabel()
        self.clockWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.clockWidget.setStyleSheet("font-size: 190pt; color: #fff; background: transparent;")
        self.layout.addWidget(self.clockWidget)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()
        self.installEventFilter(self)

    def update_clock(self):
        now = datetime.datetime.now()
        self.clockWidget.setText(now.strftime("%H:%M"))

    def show_image(self):
        self.clear_mode()
        self.mode = 'image'
        self.imageWidget = QtWidgets.QLabel()
        self.imageWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.imageWidget.setStyleSheet("background: transparent;")
        self.layout.addWidget(self.imageWidget)
        # Always use Dir/logo.png as the image
        import os
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))
        if not os.path.exists(logo_path):
            # fallback: try Dir/logo.png relative to project root
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logo.png'))
        self._image_pixmap = QtGui.QPixmap(logo_path)
        if not self._image_pixmap.isNull():
            # Hide all controls for fullscreen effect
            for i in reversed(range(self.layout.count())):
                    item = self.layout.itemAt(i)
                    widget = item.widget()
                    if widget and widget != self.imageWidget:
                        widget.hide()
                    self.setContentsMargins(0, 0, 0, 0)
                    self.imageWidget.setContentsMargins(0, 0, 0, 0)
                    self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
                    self.showFullScreen()
                    self.update_image_pixmap()
        self.installEventFilter(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.mode == 'image' and hasattr(self, '_image_pixmap') and self._image_pixmap:
            self.update_image_pixmap()

    def update_image_pixmap(self):
        if hasattr(self, '_image_pixmap') and self._image_pixmap:
            scaled = self._image_pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.imageWidget.setPixmap(scaled)

    def clear_mode(self):
        # Remove previous widgets
        if self.clockWidget:
            self.layout.removeWidget(self.clockWidget)
            self.clockWidget.deleteLater()
            self.clockWidget = None
        if self.imageWidget:
            self.layout.removeWidget(self.imageWidget)
            self.imageWidget.deleteLater()
            self.imageWidget = None
        if hasattr(self, 'timer'):
            self.timer.stop()
            del self.timer
        # Restore window state if needed
        if self.isFullScreen():
            self.showNormal()
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.FramelessWindowHint)
        self.removeEventFilter(self)

    def eventFilter(self, obj, event):
        if self.mode in ['clock', 'image'] and event.type() == QtCore.QEvent.MouseButtonPress:
            # Signal to parent to close screensaver
            if hasattr(self.parent(), 'close_screensaver'):
                self.parent().close_screensaver()
            return True
        return super().eventFilter(obj, event)
