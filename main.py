import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QGroupBox, QMessageBox, QPushButton)
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# --- CameraWorker for AI processing ---
class CameraWorker(QThread):
    frame_ready = pyqtSignal(QImage)
    detection_result = pyqtSignal(str)

    def __init__(self, parent=None):
        super(CameraWorker, self).__init__(parent)
        self._running = True

    def run(self):
        from mtcnn import MTCNN
        from tensorflow.keras.models import load_model

        try:
            model = load_model("ai/best2_mask_detector.h5")
            detector = MTCNN()
            cap = cv2.VideoCapture(0)
        except Exception as e:
            print(f"Error initializing camera or models: {e}")
            return

        while self._running:
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detections = detector.detect_faces(frame_rgb)
            current_status = "no_face"

            for detection in detections:
                x, y, width, height = detection['box']
                face_crop = frame_rgb[y:y+height, x:x+width]

                if face_crop.size == 0:
                    continue

                face_crop_resized = cv2.resize(face_crop, (224, 224))
                face_crop_resized = face_crop_resized.astype("float32") / 255.0
                face_crop_resized = np.expand_dims(face_crop_resized, axis=0)

                prediction = model.predict(face_crop_resized)[0][0]
                label = "without_mask" if prediction > 0.5 else "mask"
                current_status = label

                box_color = (0, 255, 0) if label == "mask" else (255, 0, 0)
                cv2.rectangle(frame_rgb, (x, y), (x+width, y+height), box_color, 2)
                cv2.putText(frame_rgb, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)

            self.detection_result.emit(current_status)

            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_ready.emit(qt_image.scaled(640, 480, Qt.KeepAspectRatio))

        cap.release()
        print("Camera released and thread finished.")

    def stop(self):
        """Sets the running flag to False to gracefully stop the thread."""
        self._running = False
        self.wait() # Wait for the run() method to complete


# --- Main GUI Application (Backup Version) ---
class GuardianAppGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iron Mask Guardian (Demo Mode)")
        self.setGeometry(100, 100, 1200, 600)

        # --- THIS IS THE CHANGE FOR TESTING ---
        # Force bad weather on startup.
        self.pollution_level = 150
        
        self.mask_status = "Unknown"
        self.pollution_threshold = 100

        self.init_ui()
        self.apply_styles()
        
        # We start the camera immediately in this version
        self.start_camera()
        # Set the initial UI status
        self.update_air_quality(self.pollution_level)

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left Side: Camera Feed and AI Status
        left_group_box = QGroupBox("Live Monitoring")
        left_layout = QVBoxLayout()
        left_group_box.setLayout(left_layout)
        self.camera_feed_label = QLabel("Initializing Camera...")
        self.camera_feed_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_label.setStyleSheet("background-color: black;")
        left_layout.addWidget(self.camera_feed_label)
        self.mask_status_label = QLabel("Mask Status: UNKNOWN")
        self.mask_status_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.mask_status_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.mask_status_label)

        # Right Side: Air Quality Control and Final Warning
        right_group_box = QGroupBox("System Control")
        right_layout = QVBoxLayout()
        right_group_box.setLayout(right_layout)
        self.pollution_level_label = QLabel("Air Quality Level: N/A")
        self.pollution_level_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.pollution_level_label.setAlignment(Qt.AlignCenter)
        self.final_warning_label = QLabel("System OK")
        self.final_warning_label.setFont(QFont("Arial", 32, QFont.Bold))
        self.final_warning_label.setAlignment(Qt.AlignCenter)
        self.final_warning_label.setWordWrap(True)

        # Control buttons for the demo
        self.simulate_pollution_button = QPushButton("Simulate High Pollution Event")
        self.simulate_pollution_button.setFont(QFont("Arial", 14))
        self.simulate_pollution_button.clicked.connect(self.trigger_bad_air)

        self.reset_air_button = QPushButton("Reset to Good Air")
        self.reset_air_button.setFont(QFont("Arial", 14))
        self.reset_air_button.clicked.connect(self.trigger_good_air)

        right_layout.addWidget(self.pollution_level_label)
        right_layout.addStretch(1)
        right_layout.addWidget(self.simulate_pollution_button)
        right_layout.addWidget(self.reset_air_button)
        right_layout.addStretch(1)
        right_layout.addWidget(self.final_warning_label)
        right_layout.addStretch(2)

        main_layout.addWidget(left_group_box, 2)
        main_layout.addWidget(right_group_box, 1)
        self.setLayout(main_layout)

    def start_camera(self):
        self.camera_worker = CameraWorker()
        self.camera_worker.frame_ready.connect(self.update_camera_feed)
        self.camera_worker.detection_result.connect(self.update_mask_status)
        self.camera_worker.start()

    def trigger_bad_air(self):
        """Button click handler to simulate bad air."""
        self.update_air_quality(150)

    def trigger_good_air(self):
        """Button click handler to simulate good air."""
        self.update_air_quality(50)

    def update_camera_feed(self, image):
        self.camera_feed_label.setPixmap(QPixmap.fromImage(image))

    def update_mask_status(self, status):
        self.mask_status = status
        if status == "mask":
            text, color = "Mask: DETECTED", "green"
        elif status == "without_mask":
            text, color = "Mask: NOT DETECTED", "red"
        else:
            text, color = "NO FACE DETECTED", "gray"
        self.mask_status_label.setText(text)
        self.mask_status_label.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px;")
        self.check_final_warning()

    def update_air_quality(self, value):
        self.pollution_level = value
        self.pollution_level_label.setText(f"Air Quality Level: {value}")
        self.check_final_warning()

    def check_final_warning(self):
        is_air_bad = self.pollution_level > self.pollution_threshold
        is_mask_missing = self.mask_status == "without_mask"

        if is_air_bad and is_mask_missing:
            self.final_warning_label.setText(f"WARNING!\nAir quality is poor (Level: {self.pollution_level})\nPUT ON A MASK!")
            self.final_warning_label.setStyleSheet("background-color: #ffcccc; color: #cc0000; border: 3px solid #cc0000; border-radius: 20px; padding: 10px;")
        elif is_air_bad and not is_mask_missing:
            self.final_warning_label.setText("Air quality is poor.\nGood job wearing a mask.")
            self.final_warning_label.setStyleSheet("background-color: #e6f7ff; color: #004d99; border: 3px solid #90b3cc; border-radius: 20px; padding: 10px;")
        else:
            self.final_warning_label.setText("Air Quality is GOOD.\nNo mask required.")
            self.final_warning_label.setStyleSheet("background-color: #ccffcc; color: #009900; border: 3px solid #009900; border-radius: 20px; padding: 10px;")

    def closeEvent(self, event):
        print("Close event triggered. Stopping threads...")
        self.camera_worker.stop()
        event.accept()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; font-family: 'Segoe UI', Arial, sans-serif; }
            QGroupBox { background-color: #ffffff; border: 2px solid #a0a0a0; border-radius: 10px; margin-top: 10px; font-size: 16px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }
            QPushButton { padding: 10px; background-color: #d0d0d0; border: 1px solid #a0a0a0; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #e0e0e0; }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GuardianAppGUI()
    gui.show()
    sys.exit(app.exec_())

