# main.py (only the class changed; rest stays the same)

import os
import sys
import subprocess
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QGroupBox, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot

class GuardianAppGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iron Mask Guardian (Demo Mode)")
        self.setGeometry(100, 100, 1200, 600)

        self.pollution_threshold = 100
        self.pollution_level = 150
        self.mask_status = "Unknown"
        self.ai_process = None

        self.init_ui()         # <- now exists
        self.apply_styles()    # <- now exists
        self.update_air_quality(self.pollution_level)

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left: status placeholder
        left_group = QGroupBox("Live Monitoring")
        left_layout = QVBoxLayout(left_group)

        self.camera_feed_label = QLabel("AI starts only when Air Quality > 100")
        self.camera_feed_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_label.setStyleSheet("background-color: black; color: white;")
        self.camera_feed_label.setFont(QFont("Segoe UI", 14))
        left_layout.addWidget(self.camera_feed_label)

        self.mask_status_label = QLabel("Mask Status: UNKNOWN")
        self.mask_status_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.mask_status_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.mask_status_label)

        # Right: controls
        right_group = QGroupBox("System Control")
        right_layout = QVBoxLayout(right_group)

        self.pollution_level_label = QLabel("Air Quality Level: N/A")
        self.pollution_level_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.pollution_level_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.pollution_level_label)

        right_layout.addStretch(1)
        btn_bad = QPushButton("Simulate High Pollution Event")
        btn_bad.setFont(QFont("Segoe UI", 14))
        btn_bad.clicked.connect(lambda: self.update_air_quality(150))
        right_layout.addWidget(btn_bad)

        btn_good = QPushButton("Reset to Good Air")
        btn_good.setFont(QFont("Segoe UI", 14))
        btn_good.clicked.connect(lambda: self.update_air_quality(50))
        right_layout.addWidget(btn_good)

        right_layout.addStretch(1)
        self.final_warning_label = QLabel("System OK")
        self.final_warning_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.final_warning_label.setAlignment(Qt.AlignCenter)
        self.final_warning_label.setWordWrap(True)
        right_layout.addWidget(self.final_warning_label)
        right_layout.addStretch(2)

        main_layout.addWidget(left_group, 2)
        main_layout.addWidget(right_group, 1)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; }
            QGroupBox {
                background-color: #ffffff;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }
            QPushButton {
                padding: 10px;
                background-color: #d0d0d0;
                border: 1px solid #a0a0a0;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)

    # --- AI subprocess control (unchanged from earlier) ---
    def start_ai(self):
        if self.ai_process is not None and self.ai_process.poll() is None:
            return
        project_root = os.path.dirname(__file__)
        ai_dir = os.path.join(project_root, "ai")
        ai_script = os.path.join(ai_dir, "realtime_mask_detection.py")
        try:
            self.ai_process = subprocess.Popen(
                [sys.executable, "-u", ai_script],
                cwd=ai_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            threading.Thread(target=self._stream_reader, args=(self.ai_process.stdout,), daemon=True).start()
            threading.Thread(target=self._stream_reader, args=(self.ai_process.stderr,), daemon=True).start()
            self.camera_feed_label.setText("AI running in a separate window")
        except Exception as e:
            QMessageBox.critical(self, "AI Launch Error", str(e))

    def stop_ai(self):
        if self.ai_process is not None:
            try:
                self.ai_process.terminate()
                self.ai_process.wait(timeout=3)
            except Exception:
                try:
                    self.ai_process.kill()
                except Exception:
                    pass
            finally:
                self.ai_process = None
        self.camera_feed_label.setText("AI stopped (Air Quality ≤ 100)")
        self._set_mask_status("Unknown")

    def _stream_reader(self, pipe):
        for line in iter(pipe.readline, ""):
            msg = line.strip()
            print("[AI]", msg)
            if msg.startswith("[STATUS]"):
                status = msg.split("]", 1)[1].strip()
                QMetaObject.invokeMethod(
                    self, "_update_mask_from_status",
                    Qt.QueuedConnection, Q_ARG(str, status)
                )

    @pyqtSlot(str)
    def _update_mask_from_status(self, status):
        self._set_mask_status(status)

    def _set_mask_status(self, status):
        self.mask_status = status
        if status == "mask":
            text, bg = "Mask: DETECTED", "green"
        elif status == "without_mask":
            text, bg = "Mask: NOT DETECTED", "red"
        elif status == "no_face":
            text, bg = "NO FACE DETECTED", "gray"
        else:
            text, bg = "Mask Status: UNKNOWN", "gray"
        self.mask_status_label.setText(text)
        self.mask_status_label.setStyleSheet(
            f"background-color: {bg}; color: white; padding: 5px; border-radius: 10px;"
        )
        self.check_final_warning()

    def update_air_quality(self, value):
        self.pollution_level = value
        self.pollution_level_label.setText(f"Air Quality Level: {value}")
        self.check_final_warning()
        if self.pollution_level > self.pollution_threshold:
            self.start_ai()
        else:
            self.stop_ai()

    def check_final_warning(self):
        air_bad = self.pollution_level > self.pollution_threshold
        no_mask = (self.mask_status == "without_mask")
        if air_bad and no_mask:
            msg = (f"WARNING!\nAir quality is poor (Level: {self.pollution_level})\n"
                   "PUT ON A MASK!")
            style = "background-color: #ffcccc; color: #cc0000;"
        elif air_bad:
            msg = "Air quality is poor.\nGood job wearing a mask."
            style = "background-color: #e6f7ff; color: #004d99;"
        else:
            msg = "Air Quality is GOOD.\nNo mask required."
            style = "background-color: #ccffcc; color: #009900;"
        self.final_warning_label.setText(msg)
        self.final_warning_label.setStyleSheet(f"{style} padding: 10px; border-radius: 10px;")

    def closeEvent(self, event):
        self.stop_ai()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GuardianAppGUI()
    gui.show()
    sys.exit(app.exec_())
