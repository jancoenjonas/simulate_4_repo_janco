#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <Wire.h>
#include "credentials.h"

#define RST_PIN         26  // Configurable, typically tied to a valid GPIO
#define SS_PIN          SDA // Usually pin 21 on ESP32

#define BUZZER_PIN      25  // Digital pin connected to the buzzer
#define GREEN_LED_PIN   27  // Digital pin connected to the green LED
#define YELLOW_LED_PIN  33  // Digital pin connected to the yellow LED
#define RED_LED_PIN     34  // Digital pin connected to the red LED


// RFID-RC522 instance
MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
    Serial.begin(115200);
    SPI.begin();
    mfrc522.PCD_Init();
    
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(YELLOW_LED_PIN, OUTPUT);
    pinMode(RED_LED_PIN, OUTPUT);

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println(" Connected to WiFi! Let's get started!");
}

void playBeep() {
    tone(BUZZER_PIN, 1500, 200);  // High pitched beep, 1500 Hz for 200 milliseconds
    delay(200);
    noTone(BUZZER_PIN);
}

bool sendPOSTRequest(String tagID) {
    WiFiClient client;
    if (!client.connect(serverIP, serverPort)) {
        Serial.println("Connection failed. But don't worry, we'll try again!");
        return false;
    }

    String postData = "nfc_tag=" + tagID;
    client.print("POST ");
    client.print(endpoint);
    client.println(" HTTP/1.1");
    client.println("Host: " + String(serverIP) + ":" + String(serverPort));
    client.println("Content-Type: application/x-www-form-urlencoded");
    client.print("Content-Length: ");
    client.println(postData.length());
    client.println();
    client.println(postData);

    while (client.connected() && !client.available()) delay(1); // Wait until the server responds

    String line = client.readStringUntil('\n'); // Reading the first line of the response
    client.stop();

    Serial.println("Server says: " + line); // Print server response for debugging

    return line.startsWith("OK");  // Check if the response starts with "OK"
}

void loop() {
    digitalWrite(GREEN_LED_PIN, LOW);
    digitalWrite(YELLOW_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, LOW);

    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
        String tagID = "";
        for (byte i = 0; i < mfrc522.uid.size; i++) {
            tagID += String(mfrc522.uid.uidByte[i], HEX);
        }
        tagID.toUpperCase(); // Ensure the tag ID is in uppercase to match server handling
        Serial.println("Tag UID: " + tagID);

        if (sendPOSTRequest(tagID)) {
            digitalWrite(GREEN_LED_PIN, HIGH);  // Indicate successful operation
            playBeep();  // Play a cheerful beep
            digitalWrite(GREEN_LED_PIN, LOW);
        } else {
            digitalWrite(RED_LED_PIN, HIGH);  // Indicate communication error
            tone(BUZZER_PIN, 220, 400);  // Lower tone for error
            delay(400);
            noTone(BUZZER_PIN);
            digitalWrite(RED_LED_PIN, LOW);
        }

        mfrc522.PICC_HaltA();
        mfrc522.PCD_StopCrypto1();

        Serial.println("Ready for the next tag! Bring it on!");
    }

    delay(500);
}
