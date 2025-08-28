
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "WIFI_SSID";
const char* password = "WIFI_PASSWORD";

String botToken = "7733334402:AAHruXP6p6tXFN7C1Pjp-5roLRGN58sQflk";
String chatID = "835540338";

#define ANALOG_PIN 34  
#define LED_PIN 4    

float threshold = 0.15; 

void sendTelegramMessage(String text) {
  HTTPClient http;
  String url = "https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatID + "&text=" + text;
  http.begin(url);
  http.GET();
  http.end();
}

float readDustDensity() {
  digitalWrite(LED_PIN, LOW); 
  delayMicroseconds(280);
  int raw = analogRead(ANALOG_PIN);
  delayMicroseconds(40);
  digitalWrite(LED_PIN, HIGH); 
  delayMicroseconds(9680);

  // تبدیل به ولتاژ
  float voltage = raw * (3.3 / 4095.0); // چون ESP32 رنج 0 تا 3.3 ولت داره
  // تبدیل به غلظت ذرات (mg/m^3) بر اساس دیتاشیت
  float dustDensity = 0.17 * voltage - 0.1;
  if (dustDensity < 0) dustDensity = 0;

  return dustDensity;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.println("starting");
  
}
bool isConnected = false;

void loop() {
  if (WiFi.status() == WL_CONNECTED && !isConnected) {
    Serial.println("Connected");
    Serial.println(WiFi.localIP());
    isConnected = true;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(".");
    delay(1000);
    isConnected = false;
  }
  float dust = readDustDensity();
  Serial.print("Dust Density: ");
  Serial.print(dust);
  Serial.println(" mg/m^3");

  if (dust > threshold) {
    String msg = "\n خطر الودگی هوا " + String(dust, 3) + " mg/m³";
    sendTelegramMessage(msg);
    delay(60000); 
  }

  delay(5000); 
}
