#include <SPI.h>
#include <MFRC522.h>
 #include "Wire.h"
#define RST_PIN 26   // Configurable, see typical pin layout above
#define SS_PIN  SDA  // Configurable, see typical pin layout above

#define BUZZER_PIN 25  // Digital pin connected to the buzzer

// RFID-RC522 instance
MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
    Serial.begin(115200);

    // Initialize RFID reader
    SPI.begin();
    mfrc522.PCD_Init();
    Serial.println("RFID reader initialized");

    // Initialize buzzer pin
    pinMode(BUZZER_PIN, OUTPUT);
}

void buzz(int frequency, int duration) {
    tone(BUZZER_PIN, frequency, duration);
    delay(duration);
    noTone(BUZZER_PIN);
}

void loop() {
    // Look for new RFID cards
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        delay(50);
        return;
    }

    Serial.println("RFID tag detected");

    // Print the scanned NFC tag data
    Serial.print("Tag UID: ");
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
    }
    Serial.println();

    // Play a happy sound for successful scan
    buzz(1000, 200);  // Example frequency and duration for a happy sound

    // Halt PICC
    mfrc522.PICC_HaltA();

    // Stop encryption on PCD
    mfrc522.PCD_StopCrypto1();

    delay(500); // Reduce delay between scans to 500 milliseconds
}
