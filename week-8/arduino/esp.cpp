#include <WiFi.h>
#include <SPI.h>
#include <MFRC522.h>

// WiFi network settings
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server settings (Arduino Uno R4 ESP32 IP and port)
const char* serverIP = "ARDUINO_UNO_R4_ESP32_IP";
const uint16_t port = 5000;

// RFID reader pins
#define RST_PIN 26
#define SS_PIN  5

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  String tagUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if(mfrc522.uid.uidByte[i] < 0x10) {
      tagUID += "0";
    }
    tagUID += String(mfrc522.uid.uidByte[i], HEX);
  }
  tagUID.toUpperCase();

  // Send UID to Arduino Uno R4 ESP32
  WiFiClient client;
  if (client.connect(serverIP, port)) {
    client.println(tagUID);
    client.stop();
  } else {
    Serial.println("Failed to connect to server");
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  delay(1000); // Wait a bit before next read
}
