import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QGroupBox, QSizePolicy, QMessageBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime

import requests
import json
import random

class Weather:
    def __init__(self):
        self.api_key = "ac0ec8fb30mshd1fc81b1ce21a2ep173334jsne4f952e4ff46"
        self.api_host = "open-weather13.p.rapidapi.com"
        self.base_url = f"https://{self.api_host}"

    def get_weather(self, city):
        url = f"{self.base_url}/city/{city}/EN"

        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.api_host
        }

        try:
            print(f"Fetching weather data from: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            trans_data = response.json()

            if 'cod' in trans_data and trans_data['cod'] != 200:
                print(f"API Error Response: {trans_data.get('message', 'Unknown error')}")
                return None

            weather_description = trans_data['weather'][0]['description'].capitalize()
            temperature_kelvin = trans_data['main']['temp']
            pressure = trans_data['main']['pressure']
            humidity = trans_data['main']['humidity']
            wind_speed = trans_data['wind']['speed']
            city_name = trans_data['name']

            weather_quality_index = random.randint(50, 99)
            pollution_level = random.randint(30, 180)

            return {
                "city_name": city_name,
                "weather_description": weather_description,
                "temperature": f"{temperature_kelvin}K",
                "pressure": f"{pressure} hPa",
                "humidity": f"{humidity}%",
                "wind_speed": f"{wind_speed} m/s",
                "weather_quality_index": weather_quality_index,
                "pollution_level": pollution_level
            }

        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error occurred: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"An unexpected Requests error occurred: {err}")
        except json.JSONDecodeError as errj:
            print(f"JSON Decode Error: {errj} - Response was: {response.text[:200]}")
        except Exception as e:
            print(f"An unexpected error occurred in Weather.get_weather: {e}")
        return None


class WeatherAppGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather and Pollution Monitor")
        self.setGeometry(100, 100, 900, 500)

        self.CITY = "Sirjan"

        try:
            self.weather_api_handler = Weather()
        except Exception as e:
            QMessageBox.critical(self, "API Initialization Error",
                                 f"Failed to initialize Weather class: {e}\n"
                                 "Please check your class definition.")
            sys.exit(1)

        self.init_ui()
        self.apply_styles()
        self.start_time_update()
        self.start_weather_update()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # --- Weather Information Section ---
        weather_group_box = QGroupBox("Current Weather")
        weather_layout = QVBoxLayout()
        weather_group_box.setLayout(weather_layout)
        weather_group_box.setObjectName("weatherGroupBox")

        # Time Display Label
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.time_label.setObjectName("timeDisplayLabel")
        weather_layout.addWidget(self.time_label)
        weather_layout.addSpacing(15)

        # New: City Name Display Label
        self.city_name_label = QLabel(f"City: {self.CITY}") # Initial text, will be updated
        self.city_name_label.setAlignment(Qt.AlignCenter)
        self.city_name_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.city_name_label.setObjectName("cityDisplayLabel") # Object name for styling
        weather_layout.addWidget(self.city_name_label)
        weather_layout.addSpacing(15) # Add some space below the city name

        self.temperature = "N/A"
        self.humidity = "N/A"
        self.pressure = "N/A"
        self.wind_speed = "N/A"
        self.weather_quality_index = "N/A"
        self.weather_description = "N/A"

        self.temp_label = QLabel(f"Temperature: {self.temperature}")
        self.temp_label.setObjectName("dataLabel")
        weather_layout.addWidget(self.temp_label)

        self.humidity_label = QLabel(f"Humidity: {self.humidity}")
        self.humidity_label.setObjectName("dataLabel")
        weather_layout.addWidget(self.humidity_label)

        self.pressure_label = QLabel(f"Pressure: {self.pressure}")
        self.pressure_label.setObjectName("dataLabel")
        weather_layout.addWidget(self.pressure_label)

        self.wind_speed_label = QLabel(f"Wind Speed: {self.wind_speed}")
        self.wind_speed_label.setObjectName("dataLabel")
        weather_layout.addWidget(self.wind_speed_label)

        self.weather_desc_label = QLabel(f"Description: {self.weather_description}")
        self.weather_desc_label.setObjectName("dataLabel")
        weather_layout.addWidget(self.weather_desc_label)

        self.quality_index_label = QLabel(f"Weather Quality Index: {self.weather_quality_index}")
        self.quality_index_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.quality_index_label.setAlignment(Qt.AlignCenter)
        self.quality_index_label.setObjectName("qualityIndexLabel")
        weather_layout.addStretch(1)
        weather_layout.addWidget(self.quality_index_label)
        weather_layout.addStretch(1)

        main_layout.addWidget(weather_group_box, 2)

        # --- Pollution Warning Section ---
        pollution_group_box = QGroupBox("Air Quality Status")
        pollution_layout = QVBoxLayout()
        pollution_group_box.setLayout(pollution_layout)
        pollution_group_box.setObjectName("pollutionGroupBox")

        self.pollution_level = 0
        self.pollution_threshold = 100

        self.pollution_warning_label = QLabel("")
        self.pollution_warning_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.pollution_warning_label.setAlignment(Qt.AlignCenter)
        self.pollution_warning_label.setWordWrap(True)
        self.pollution_warning_label.setObjectName("pollutionWarningLabel")

        pollution_layout.addStretch(1)
        pollution_layout.addWidget(self.pollution_warning_label)
        pollution_layout.addStretch(1)

        main_layout.addWidget(pollution_group_box, 1)

        self.setLayout(main_layout)

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.time_label.setText(f"Current Time: {current_time}")

    def start_time_update(self):
        self.timer_time = QTimer(self)
        self.timer_time.timeout.connect(self.update_time)
        self.timer_time.start(1000)
        self.update_time()

    def update_weather_data(self):
        print(f"Attempting to fetch weather data for {self.CITY}...")
        weather_data = self.weather_api_handler.get_weather(self.CITY)

        if weather_data:
            print("Weather data fetched successfully. Updating UI...")
            # Update internal variables from the API class
            self.city_name = weather_data.get("city_name", "N/A") # Get city name from API
            self.temperature = weather_data.get("temperature", "N/A")
            self.humidity = weather_data.get("humidity", "N/A")
            self.pressure = weather_data.get("pressure", "N/A")
            self.wind_speed = weather_data.get("wind_speed", "N/A")
            self.weather_description = weather_data.get("weather_description", "N/A")
            self.weather_quality_index = weather_data.get("weather_quality_index", "N/A")
            self.pollution_level = weather_data.get("pollution_level", 0)

            # Update GUI labels
            self.city_name_label.setText(f"City: {self.city_name}") # Update city name label
            self.temp_label.setText(f"Temperature: {self.temperature}")
            self.humidity_label.setText(f"Humidity: {self.humidity}")
            self.pressure_label.setText(f"Pressure: {self.pressure}")
            self.wind_speed_label.setText(f"Wind Speed: {self.wind_speed}")
            self.weather_desc_label.setText(f"Description: {self.weather_description}")
            self.quality_index_label.setText(f"Weather Quality Index: {self.weather_quality_index}")

            self.update_pollution_status()
            self.apply_styles()
        else:
            print("Failed to fetch weather data or city not found.")
            QMessageBox.warning(self, "Weather Data Error",
                                f"Failed to retrieve latest weather data for {self.CITY}. "
                                "Check connection, city name, or API key/rate limits.")
            # Set labels to N/A on error
            self.city_name_label.setText(f"City: N/A ({self.CITY})") # Indicate city tried
            self.temp_label.setText("Temperature: N/A")
            self.humidity_label.setText("Humidity: N/A")
            self.pressure_label.setText("Pressure: N/A")
            self.wind_speed_label.setText("Wind Speed: N/A")
            self.weather_desc_label.setText("Description: N/A")
            self.quality_index_label.setText("Weather Quality Index: N/A")
            self.pollution_level = 0
            self.update_pollution_status()
            self.apply_styles()

    def start_weather_update(self):
        self.timer_weather = QTimer(self)
        self.timer_weather.timeout.connect(self.update_weather_data)
        self.timer_weather.start(300000) # 5 minutes
        self.update_weather_data()

    def update_pollution_status(self):
        if self.pollution_level > self.pollution_threshold:
            self.pollution_warning_label.setText(
                f"WARNING: AIR QUALITY IS BAD!\n(Level: {self.pollution_level})"
            )
        elif self.pollution_level > 0:
            self.pollution_warning_label.setText(
                f"Air Quality is GOOD\n(Level: {self.pollution_level})"
            )
        else:
            self.pollution_warning_label.setText("Air Quality: N/A")

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QGroupBox {
                background-color: #ffffff;
                border: 2px solid #a0a0a0;
                border-radius: 10px;
                margin-top: 10px;
                font-size: 16px;
                font-weight: bold;
                color: #333333;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #e0e0e0;
                border-radius: 5px;
            }

            #weatherGroupBox {
                background-color: #e6f7ff;
                border: 2px solid #90b3cc;
            }

            #pollutionGroupBox {
                background-color: #ffe6e6;
                border: 2px solid #cc9090;
            }

            QLabel#timeDisplayLabel {
                background-color: #cceeff;
                color: #004d99;
                border: 2px solid #80c0ff;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
                font-size: 20px;
                font-weight: bold;
            }

            /* New Style for City Display Label */
            QLabel#cityDisplayLabel {
                background-color: #e0f2f7; /* Slightly lighter blue */
                color: #005a80; /* Darker blue text */
                border: 2px solid #80c0ff;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
                font-size: 20px;
                font-weight: bold;
            }


            QLabel#dataLabel {
                font-size: 16px;
                color: #333333;
                padding: 5px;
                margin-bottom: 3px;
                border-bottom: 1px dashed #cccccc;
            }

            QLabel#qualityIndexLabel {
                font-size: 28px;
                font-weight: bold;
                color: #0066cc;
                background-color: #ccedff;
                border: 2px solid #0066cc;
                border-radius: 15px;
                padding: 10px;
                margin: 10px;
            }

            QLabel#pollutionWarningLabel {
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
                border-radius: 20px;
            }
        """)

        if self.pollution_level != "N/A" and self.pollution_level > self.pollution_threshold:
            self.pollution_warning_label.setStyleSheet("""
                QLabel#pollutionWarningLabel {
                    background-color: #ffcccc;
                    color: #cc0000;
                    border: 3px solid #cc0000;
                }
            """)
        elif self.pollution_level != "N/A" and self.pollution_level > 0:
            self.pollution_warning_label.setStyleSheet("""
                QLabel#pollutionWarningLabel {
                    background-color: #ccffcc;
                    color: #009900;
                    border: 3px solid #009900;
                }
            """)
        else:
             self.pollution_warning_label.setStyleSheet("""
                QLabel#pollutionWarningLabel {
                    background-color: #e0e0e0;
                    color: #666666;
                    border: 3px solid #999999;
                }
            """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = WeatherAppGUI()
    gui.show()
    sys.exit(app.exec_())