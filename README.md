# IronMaskGuardiano-proj
🎯 A smart system to detect air quality (dust level) and mask compliance in industrial environments using AI and ESP32.

## 📌 Overview

This project uses:
- An **ESP32 + Dust Sensor (GP2Y1010AU0F)** to monitor air quality
- A **Camera + AI model** to detect if workers are wearing medical masks
- A **Flask server** to receive data and trigger alerts if air is unhealthy and no mask is detected

- 
---

## 🚀 How It Works (Basic Logic)

1. **ESP32** reads dust level from GP2Y1010 sensor
2. Sends the PM level to Flask server via Wi-Fi (JSON)
3. **Camera + AI model** detects if person is wearing a mask
4. If air quality is bad **AND** mask is not detected → system logs or triggers alert

---

## ✅ Getting Started

### Requirements
- Python 3.8+
- Flask
- OpenCV
- TensorFlow/Keras
- Arduino IDE for ESP32

### Run AI Model

cd cv/
python mask_detection.py


## 👥 Team Members & Roles
- **Reza (rezajahanshahi)** — AI Engineer: mask detection using OpenCV
- **Matin (@matinbaha)** — 
- **Aria (@poodius)** — Hardware Engineer: ESP32 & dust sensor

## 🗂️ Folder Structure (To Create)
- `/cv/` → AI code
- `/esp32/` → Hardware code
- `/server/` → Data receiving & alert logic (Flask)
- `/docs/` → Plans, sketches, references

## ✅ Current To-Dos (Start Here!)
### Reza (AI)
- Create `/cv/mask_detection.py`
- Use HaarCascade or MobileNet model to detect mask
- Save model (or link to it) in the folder

### Aria (Hardware)
- Set up wiring for GP2Y1010AU0F with ESP32
- Create `/esp32/sensor_reader.ino` that reads dust and prints values
- Plan how to send data via Wi-Fi (JSON)

### Matin (Integrator)
- Create `/server/flask_receiver.py` that:
  - Accepts dust + mask data
  - Triggers message/alert if dust is high & no mask
- Set up repo structure, Trello board, and tasks
