#include <SPI.h>
#include <MFRC522.h>
#include "Wire.h"

#define RST_PIN       26
#define SS_PIN        SDA

#define BUZZER_PIN    25
#define GREEN_LED_PIN 22  // Pin for the green LED
#define ORANGE_LED_PIN 23 // Pin for the orange LED
#define RED_LED_PIN   24  // Pin for the red LED

// RFID-RC522 instance
MFRC522 mfrc522(SS_PIN, RST_PIN);

unsigned long previousMillis = 0;  // Stores last time LED was updated

void setup() {
    Serial.begin(115200);

    // Initialize SPI interface for RFID reader
    SPI.begin();
    mfrc522.PCD_Init();
    Serial.println("RFID reader initialized");

    // Initialize buzzer and LED pins
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(ORANGE_LED_PIN, OUTPUT);
    pinMode(RED_LED_PIN, OUTPUT);
}

void buzz(int frequency, int duration) {
    tone(BUZZER_PIN, frequency, duration);
    delay(duration);
    noTone(BUZZER_PIN);
}

void loop() {
    unsigned long currentMillis = millis();

    // Look for new RFID cards
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        digitalWrite(GREEN_LED_PIN, LOW);
        digitalWrite(ORANGE_LED_PIN, LOW);
        digitalWrite(RED_LED_PIN, HIGH);  // Red LED for error/no card
        return;
    }

    // Indicate processing
    digitalWrite(ORANGE_LED_PIN, HIGH); // Orange LED for processing
    delay(100);  // Mimic processing time
    digitalWrite(ORANGE_LED_PIN, LOW);

    Serial.println("RFID tag detected");

    // Print the scanned NFC tag data
    Serial.print("Tag UID: ");
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
    }
    Serial.println();

    // Play a happy sound for successful scan
    buzz(1000, 200);
    digitalWrite(GREEN_LED_PIN, HIGH);  // Green LED for success
    delay(200);
    digitalWrite(GREEN_LED_PIN, LOW);

    // Halt PICC and stop encryption
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();

    // Wait before next scan
    if (currentMillis - previousMillis >= 500) {
        previousMillis = currentMillis;
    }
}
