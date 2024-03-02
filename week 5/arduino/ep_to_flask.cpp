#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include "Wire.h"
#include "secret.h"

#define RST_PIN 26  // Configurable, see typical pin layout above
#define SS_PIN  SDA  // Configurable, see typical pin layout above

// WiFi credentials


// RFID-RC522 instance
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Flask server URL
const char* serverUrl = "http://172.20.10.4:5001/nfc";

void setup() {
    Serial.begin(115200);

    // Initialize WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    // Initialize RFID reader
    SPI.begin();
    mfrc522.PCD_Init();
    Serial.println("RFID reader initialized");
}

void loop() {
    // Look for new RFID cards
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        delay(50);
        return;
    }

    Serial.println("RFID tag detected");

    // Prepare tag data for HTTP POST request
    String tagData = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        tagData += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
        tagData += String(mfrc522.uid.uidByte[i], HEX);
    }
    tagData.toUpperCase();

    // Send tag data to Flask server
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String httpRequestData = "nfc_tag=" + tagData;

    int httpResponseCode = http.POST(httpRequestData);
    if (httpResponseCode > 0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
    }
    else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
    }
    http.end();

    // Halt PICC
    mfrc522.PICC_HaltA();

    // Stop encryption on PCD
    mfrc522.PCD_StopCrypto1();

    delay(2000); // Wait a bit before reading again
}

