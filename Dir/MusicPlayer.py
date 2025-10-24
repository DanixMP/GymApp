from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
import os
import sys
import shutil
from pathlib import Path


def _get_writable_app_dir() -> Path:
    """Return a writable per-user application data directory."""
    appdata = os.getenv('APPDATA') or os.getenv('LOCALAPPDATA')
    base_dir = Path(appdata) if appdata else (Path.home() / '.gym_app')
    app_dir = base_dir / 'Gym'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def _resolve_music_dir() -> str:
    """Resolve the persistent music directory, seeding from bundled assets on first run."""
    music_dir = _get_writable_app_dir() / 'music'
    if not music_dir.exists():
        music_dir.mkdir(parents=True, exist_ok=True)
    # If empty, try to copy bundled demo music
    try:
        has_files = any(music_dir.iterdir())
    except Exception:
        has_files = True
    if not has_files:
        candidates = [Path(__file__).parent / 'music']
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            candidates.append(Path(meipass) / 'Dir' / 'music')
            candidates.append(Path(meipass) / 'music')
        for src in candidates:
            if src.exists():
                try:
                    for fname in os.listdir(str(src)):
                        if fname.lower().endswith(('.mp3', '.wav', '.ogg')):
                            shutil.copy2(str(src / fname), str(music_dir / fname))
                except Exception:
                    pass
                break
    return str(music_dir)


class ConfirmDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, title="", message="", status="warning", confirm_text="تایید", cancel_text="انصراف"):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        layout = QtWidgets.QVBoxLayout(self)
        container = QtWidgets.QFrame()
        container.setStyleSheet(
            """
            QFrame { background-color: white; border-radius: 20px; border: 2px solid #eee; }
            """
        )
        v = QtWidgets.QVBoxLayout(container)

        icon_label = QtWidgets.QLabel()
        icon_size = 48
        color = "#ff9800" if status == "warning" else ("#d32f2f" if status == "error" else "#009966")
        icon = "!" if status == "warning" else ("✕" if status == "error" else "✓")
        icon_label.setStyleSheet(f"QLabel {{ color: {color}; background-color: {color}22; border-radius: {icon_size//2}px; font-size: 32px; font-weight: bold; padding: 10px; }}")
        icon_label.setFixedSize(icon_size, icon_size)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setText(icon)

        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("QLabel { color: #333; font-size: 22px; font-weight: bold; font-family: 'Dubai Medium'; }")

        header = QtWidgets.QHBoxLayout()
        header.addWidget(icon_label, alignment=Qt.AlignRight)
        header.addWidget(title_label, alignment=Qt.AlignRight)
        header.addStretch()
        v.addLayout(header)

        msg_label = QtWidgets.QLabel(message)
        msg_label.setStyleSheet("QLabel { color: #666; font-size: 16px; font-family: 'Dubai Medium'; }")
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        v.addWidget(msg_label)

        buttons = QtWidgets.QHBoxLayout()
        confirm_btn = QtWidgets.QPushButton(confirm_text)
        cancel_btn = QtWidgets.QPushButton(cancel_text)
        confirm_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border: none; border-radius: 10px; padding: 8px 24px; font-size: 14px; font-family: 'Dubai Medium'; }")
        cancel_btn.setStyleSheet("QPushButton { background-color: #888; color: white; border: none; border-radius: 10px; padding: 8px 24px; font-size: 14px; font-family: 'Dubai Medium'; }")
        confirm_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(confirm_btn)
        buttons.addWidget(cancel_btn)
        v.addLayout(buttons)

        layout.addWidget(container)
        self.setFixedSize(420, 220)


class MusicPlayer(QtWidgets.QWidget):
    def stop_music(self):
        self.player.stop()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = QMediaPlayer()
        self.playlist = []
        self.current_track_index = -1
        self.music_file = None
        self.init_ui()
        self.reload_playlist()
    def init_ui(self):
        # Outer layout for this widget
        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # White box frame
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("background: white; border-radius: 22px; padding: 18px 12px 12px 12px;")
        frame_layout = QtWidgets.QVBoxLayout(frame)
        frame_layout.setSpacing(12)

        title = QtWidgets.QLabel("<b>پخش موسیقی</b>")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18pt; color: #3c096c; font-family: 'Dubai Medium'; margin-bottom: 8px; background-color:#e7c6ff")
        frame_layout.addWidget(title)

        # Playlist and controls row
        row = QtWidgets.QHBoxLayout()
        self.playlist_combo = QtWidgets.QComboBox()
        self.playlist_combo.setStyleSheet("font-size: 12pt; min-width: 200px; padding: 6px 12px; border-radius: 8px;")
        self.playlist_combo.currentIndexChanged.connect(self.select_track)
        row.addWidget(self.playlist_combo, 2)

        self.add_btn = QtWidgets.QPushButton("➕ افزودن موسیقی")
        self.add_btn.setStyleSheet("background: #009966; color: #fff; font-weight: bold; border-radius: 8px; padding: 6px 16px; font-size: 11pt; font-family: 'Dubai Medium'; margin-right: 8px;")
        self.add_btn.clicked.connect(self.add_files_to_playlist)
        row.addWidget(self.add_btn, 1)

        self.remove_btn = QtWidgets.QPushButton("🗑️ حذف موسیقی")
        self.remove_btn.setStyleSheet("background: #d32f2f; color: #fff; font-weight: bold; border-radius: 8px; padding: 6px 16px; font-size: 11pt; font-family: 'Dubai Medium';")
        self.remove_btn.clicked.connect(self.remove_selected_music)
        row.addWidget(self.remove_btn, 1)

        frame_layout.addLayout(row)

        controls = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton("⏮️")
        self.play_btn = QtWidgets.QPushButton("▶️")
        self.pause_btn = QtWidgets.QPushButton("⏸️")
        self.next_btn = QtWidgets.QPushButton("⏭️")
        for btn in [self.prev_btn, self.play_btn, self.pause_btn, self.next_btn]:
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("font-size: 18pt; border-radius: 20px; background: #7209b7; color: #fff; min-height: 32px;min-width: 32px;")
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.next_btn)
        frame_layout.addLayout(controls)

        self.play_btn.clicked.connect(self.play_music)
        self.pause_btn.clicked.connect(self.pause_music)
        self.next_btn.clicked.connect(self.next_track)
        self.prev_btn.clicked.connect(self.prev_track)

        # Music status and progress bar row
        progress_row = QtWidgets.QHBoxLayout()
        self.time_label = QtWidgets.QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("font-size: 10pt; color: #3c096c; min-width: 90px; font-family: 'Dubai Medium';")
        progress_row.addWidget(self.time_label)
        self.progress_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setStyleSheet("margin: 8px 0; height: 12px;")
        self.progress_slider.sliderMoved.connect(self.set_track_position)
        progress_row.addWidget(self.progress_slider, 1)
        frame_layout.addLayout(progress_row)

        self.player.positionChanged.connect(self.update_progress)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        self.track_duration = 0

        # Add the white frame to the outer layout
        outer_layout.addWidget(frame)

    def add_files_to_playlist(self):
        music_dir = _resolve_music_dir()
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "انتخاب فایل‌های موسیقی", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if files:
            for f in files:
                f = os.path.abspath(f)
                fname = os.path.basename(f)
                dest = os.path.join(music_dir, fname)
                if not os.path.exists(dest):
                    try:
                        shutil.copy2(f, dest)
                    except Exception as e:
                        QtWidgets.QMessageBox.warning(self, "خطا", f"امکان کپی فایل {fname} وجود ندارد: {e}")
                        continue
            self.reload_playlist()

    def remove_selected_music(self):
        idx = self.playlist_combo.currentIndex()
        if 0 <= idx < len(self.playlist):
            fpath = self.playlist[idx]
            fname = os.path.basename(fpath)
            dlg = ConfirmDialog(self, title="تایید حذف", message=f"آیا از حذف «{fname}» مطمئن هستید؟", status="warning", confirm_text="حذف", cancel_text="انصراف")
            if dlg.exec_() == QtWidgets.QDialog.Accepted:
                try:
                    os.remove(fpath)
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "خطا", f"امکان حذف فایل وجود ندارد: {e}")
                self.reload_playlist()

    def reload_playlist(self):
        music_dir = _resolve_music_dir()
        self.playlist.clear()
        self.playlist_combo.clear()
        if os.path.exists(music_dir):
            for fname in os.listdir(music_dir):
                if fname.lower().endswith(('.mp3', '.wav', '.ogg')):
                    fpath = os.path.join(music_dir, fname)
                    self.playlist.append(fpath)
                    self.playlist_combo.addItem(fname, fpath)
        if self.playlist:
            self.current_track_index = 0
            self.load_track(0)

    def select_track(self, idx):
        if 0 <= idx < len(self.playlist):
            # Always play if this was triggered by handle_media_status (looping)
            # Use a flag to distinguish user/manual vs programmatic change
            if hasattr(self, '_auto_play_next') and self._auto_play_next:
                auto_play = True
                self._auto_play_next = False
            else:
                auto_play = False
            self.current_track_index = idx
            self.load_track(idx)
            if auto_play:
                self.player.play()

    def load_track(self, idx):
        if 0 <= idx < len(self.playlist):
            self.music_file = self.playlist[idx]
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music_file)))
            self.progress_slider.setValue(0)

    def play_music(self):
        if self.music_file:
            self.player.play()
        elif self.playlist:
            # If nothing loaded but playlist exists, start from first track
            self.current_track_index = 0
            self.load_track(0)
            self.player.play()

    def pause_music(self):
        self.player.pause()

    def next_track(self):
        if self.playlist:
            next_idx = (self.current_track_index + 1) % len(self.playlist)
            self.playlist_combo.setCurrentIndex(next_idx)
            # If not playing, start playback automatically
            if self.player.state() != QMediaPlayer.PlayingState:
                self.play_music()

    def prev_track(self):
        if self.playlist:
            prev_idx = (self.current_track_index - 1) % len(self.playlist)
            self.playlist_combo.setCurrentIndex(prev_idx)
            # If not playing, start playback automatically
            if self.player.state() != QMediaPlayer.PlayingState:
                self.play_music()

    def update_progress(self, position):
        duration = self.track_duration if self.track_duration > 0 else self.player.duration()
        if duration > 0:
            self.progress_slider.blockSignals(True)
            self.progress_slider.setValue(int(position * 100 / duration))
            self.progress_slider.blockSignals(False)
            # Update time label
            cur_min, cur_sec = divmod(position // 1000, 60)
            total_min, total_sec = divmod(duration // 1000, 60)
            self.time_label.setText(f"{int(cur_min):02}:{int(cur_sec):02} / {int(total_min):02}:{int(total_sec):02}")
        else:
            self.progress_slider.setValue(0)
            self.time_label.setText("00:00 / 00:00")

    def update_duration(self, duration):
        self.progress_slider.setEnabled(duration > 0)
        self.track_duration = duration
        # Update label immediately if possible
        position = self.player.position()
        cur_min, cur_sec = divmod(position // 1000, 60)
        total_min, total_sec = divmod(duration // 1000, 60)
        self.time_label.setText(f"{int(cur_min):02}:{int(cur_sec):02} / {int(total_min):02}:{int(total_sec):02}")

    def set_track_position(self, value):
        duration = self.player.duration()
        if duration > 0:
            self.player.setPosition(int(duration * value / 100))

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia and self.playlist:
            # Robust looping: directly load and play next track, update combo for UI only
            next_idx = (self.current_track_index + 1) % len(self.playlist)
            self.current_track_index = next_idx
            self.load_track(next_idx)
            self.player.play()
            # Update combo box for UI sync, block signals to avoid recursion
            self.playlist_combo.blockSignals(True)
            self.playlist_combo.setCurrentIndex(next_idx)
            self.playlist_combo.blockSignals(False)
