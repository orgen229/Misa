#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

#define DHTPIN 22
#define RELAY_PIN 23
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// Wi-Fi hotspot
const char* WIFI_SSID = "iPhone (Егор)";
const char* WIFI_PASSWORD = "slon229337";

// Flask server on Windows → VirtualBox port forwarding
const char* SERVER_URL = "http://172.20.10.3:5000/api/data";

const unsigned long MEASUREMENT_INTERVAL = 5000;
unsigned long lastMeasurementTime = 0;

// Temperature thresholds
const float FAN_ON_TEMP = 33.0;
const float FAN_OFF_TEMP = 32.0;

bool fanState = false;

// Если реле active LOW:
// LOW  = relay ON
// HIGH = relay OFF
void setFan(bool state) {
  fanState = state;

  if (fanState) {
    digitalWrite(RELAY_PIN, LOW);   // fan ON
  } else {
    digitalWrite(RELAY_PIN, HIGH);  // fan OFF
  }
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected");
    Serial.print("ESP32 IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connection failed");
  }
}

void sendDataToServer(float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectToWiFi();
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"temperature\":";
    json += String(temperature, 2);
    json += ",";
    json += "\"humidity\":";
    json += String(humidity, 2);
    json += ",";
    json += "\"unit_temperature\":\"C\",";
    json += "\"unit_humidity\":\"%\",";
    json += "\"sensor\":\"DHT11\",";
    json += "\"fan_state\":\"";
    json += fanState ? "ON" : "OFF";
    json += "\"";
    json += "}";

    Serial.println("Sending JSON:");
    Serial.println(json);

    int httpResponseCode = http.POST(json);

    Serial.print("HTTP response code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response:");
      Serial.println(response);
    } else {
      Serial.print("HTTP POST failed: ");
      Serial.println(http.errorToString(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("Cannot send data. WiFi not connected.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 DHT11 HTTP sender started");

  pinMode(RELAY_PIN, OUTPUT);
  setFan(false); // fan OFF at startup

  dht.begin();
  connectToWiFi();
}

void loop() {
  unsigned long currentTime = millis();

  if (currentTime - lastMeasurementTime >= MEASUREMENT_INTERVAL) {
    lastMeasurementTime = currentTime;

    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Failed to read from DHT11");
      return;
    }

    // Fan control with hysteresis
    if (!fanState && temperature >= FAN_ON_TEMP) {
      setFan(true);
    }

    if (fanState && temperature <= FAN_OFF_TEMP) {
      setFan(false);
    }

    Serial.println("----------------------");
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" C");

    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

    Serial.print("Fan state: ");
    Serial.println(fanState ? "ON" : "OFF");

    sendDataToServer(temperature, humidity);
  }
}