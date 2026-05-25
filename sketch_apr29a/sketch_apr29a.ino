#define RELAY_PIN 23

void setup() {
  Serial.begin(115200);
  Serial.println("Open drain relay test");
}

void loop() {
  Serial.println("Relay ON");
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);   // тянем IN к GND
  delay(3000);

  Serial.println("Relay OFF");
  pinMode(RELAY_PIN, INPUT);      // отпускаем IN
  delay(3000);
}