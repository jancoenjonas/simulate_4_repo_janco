#include <SPI.h>
#include <MFRC522.h>
#include "Wire.h"

#define RST_PIN 26  // Configurable, see typical pin layout above
#define SS_PIN  SDA  // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance

void setup() {
    Serial.begin(115200); // Initialize serial communications with the PC
    SPI.begin();          // Init SPI bus
    mfrc522.PCD_Init();   // Init MFRC522 card
    Serial.println("RFID reader initialized. Waiting for NFC tag...");
}

void loop() {
    // Look for new RFID cards
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        delay(50); // Wait a bit before trying again
        return;
    }

    // Show UID on serial monitor
    Serial.print("NFC Tag UID:");
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
    }
    Serial.println();

    // Halt PICC and stop encryption on PCD
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();

    delay(2000); // Wait a bit before reading again
}
