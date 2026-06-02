#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

#define DHTPIN 22
#define RELAY_PIN 23
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ===== Wi-Fi settings =====
// Before uploading, replace these values with your own Wi-Fi credentials.
const char* WIFI_SSID = "iPhone (Егор)";
const char* WIFI_PASSWORD = "slon229337";

// ===== Server settings =====
// Example: http://172.20.10.3:5000
const char* SERVER_BASE_URL = "http://172.20.10.3:5000";
const char* DATA_ENDPOINT = "/api/data";
const char* CONFIG_ENDPOINT = "/api/config";

unsigned long measurementInterval = 5000;
unsigned long lastMeasurementTime = 0;
unsigned long lastConfigTime = 0;
const unsigned long CONFIG_INTERVAL = 5000;

float fanOnTemp = 33.0;
float fanOffTemp = 32.0;

bool fanState = false;
bool systemOpen = false;
bool monitoringActive = false;


// Relay module is active LOW.
// This relay works better in open-drain style:
// ON  = GPIO pulls IN to GND
// OFF = GPIO is released as INPUT
void setFan(bool state) {
  fanState = state;

  if (fanState) {
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);   // fan ON
  } else {
    pinMode(RELAY_PIN, INPUT);      // fan OFF
  }
}


float extractJsonNumber(String json, String key, float defaultValue) {
  String pattern = "\"" + key + "\":";
  int start = json.indexOf(pattern);

  if (start < 0) {
    return defaultValue;
  }

  start += pattern.length();
  int end = json.indexOf(",", start);

  if (end < 0) {
    end = json.indexOf("}", start);
  }

  if (end < 0) {
    return defaultValue;
  }

  String value = json.substring(start, end);
  value.trim();

  return value.toFloat();
}


bool extractJsonBool(String json, String key, bool defaultValue) {
  String pattern = "\"" + key + "\":";
  int start = json.indexOf(pattern);

  if (start < 0) {
    return defaultValue;
  }

  start += pattern.length();
  String value = json.substring(start, start + 5);
  value.trim();

  if (value.startsWith("true")) {
    return true;
  }

  if (value.startsWith("false")) {
    return false;
  }

  return defaultValue;
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


String buildUrl(const char* endpoint) {
  return String(SERVER_BASE_URL) + String(endpoint);
}


void fetchConfigFromServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectToWiFi();
  }

  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  HTTPClient http;
  String url = buildUrl(CONFIG_ENDPOINT);

  http.begin(url);
  int responseCode = http.GET();

  if (responseCode == 200) {
    String response = http.getString();

    fanOnTemp = extractJsonNumber(response, "fan_on_threshold", fanOnTemp);
    fanOffTemp = extractJsonNumber(response, "fan_off_threshold", fanOffTemp);
    measurementInterval = (unsigned long)extractJsonNumber(response, "measurement_interval", measurementInterval);

    systemOpen = extractJsonBool(response, "system_open", systemOpen);
    monitoringActive = extractJsonBool(response, "monitoring_active", monitoringActive);

    Serial.println("Config updated from server:");
    Serial.print("Fan ON threshold: ");
    Serial.println(fanOnTemp);
    Serial.print("Fan OFF threshold: ");
    Serial.println(fanOffTemp);
    Serial.print("Measurement interval: ");
    Serial.println(measurementInterval);
    Serial.print("System open: ");
    Serial.println(systemOpen ? "true" : "false");
    Serial.print("Monitoring active: ");
    Serial.println(monitoringActive ? "true" : "false");
  } else {
    Serial.print("Config GET failed. HTTP code: ");
    Serial.println(responseCode);
  }

  http.end();

  if (!systemOpen || !monitoringActive) {
    setFan(false);
  }
}


void sendDataToServer(float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectToWiFi();
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = buildUrl(DATA_ENDPOINT);

    http.begin(url);
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

  pinMode(RELAY_PIN, INPUT);
  setFan(false);

  dht.begin();
  connectToWiFi();
}


void loop() {
  unsigned long currentTime = millis();

  if (currentTime - lastConfigTime >= CONFIG_INTERVAL) {
    lastConfigTime = currentTime;
    fetchConfigFromServer();
  }

  if (currentTime - lastMeasurementTime >= measurementInterval) {
    lastMeasurementTime = currentTime;

    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Failed to read from DHT11");
      return;
    }

    if (systemOpen && monitoringActive) {
      if (!fanState && temperature >= fanOnTemp) {
        setFan(true);
      }

      if (fanState && temperature <= fanOffTemp) {
        setFan(false);
      }
    } else {
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
