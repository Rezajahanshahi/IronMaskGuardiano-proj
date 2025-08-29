import cv2
import numpy as np
from mtcnn import MTCNN
from tensorflow.keras.models import load_model

# Load your trained mask detection model
model = load_model("best2_mask_detector.h5")
print("Model loaded successfully!")

# Initialize the MTCNN face detector
detector = MTCNN()

# Open the webcam video stream
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No frame captured")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    detections = detector.detect_faces(frame_rgb)

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
        print(f"[STATUS] {label}", flush=True)  # <= add this line

        # Change bounding box color based on prediction
        box_color = (0, 255, 0) if label == "mask" else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+width, y+height), box_color, 2)
        cv2.putText(frame, f"{label}: {prediction:.2f}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)
        

    cv2.imshow("Real-Time Mask Detection", frame)

    # Check if the window is still open. If it was closed manually, break the loop.
    if cv2.getWindowProperty("Real-Time Mask Detection", cv2.WND_PROP_VISIBLE) < 1:
        break

    # Break if 'q' is pressed.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
