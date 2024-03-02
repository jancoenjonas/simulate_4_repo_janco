#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 9     // Replace with your actual RST pin for the NFC reader
#define SS_PIN  21    // Replace with your actual SDA pin for the NFC reader

// Create MFRC522 instance
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Set the LCD I2C address to 0x27 or 0x3F depending on your module
LiquidCrystal_I2C lcd(0x27, 16, 2); // 16 columns and 2 rows for the LCD

void setup() {
    Serial.begin(9600);  // Initialize serial communications with the PC
    while (!Serial);     // Do nothing if no serial port is opened

    SPI.begin();         // Init SPI bus
    mfrc522.PCD_Init();  // Init MFRC522 card

    Wire.begin();        // Init I2C bus for the LCD

    // Initialize the LCD
    lcd.init();
    lcd.backlight();

    // Show a welcome message on the LCD
    lcd.setCursor(0, 0); // Set the cursor to column 0, row 0
    lcd.print("NFC Reader");
    lcd.setCursor(0, 1); // Move to the second row
    lcd.print("Ready");
    delay(2000);         // Wait for 2 seconds
    lcd.clear();         // Clear the display
}

void loop() {
    // Reset the loop if no new card is present on the sensor/reader
    if (!mfrc522.PICC_IsNewCardPresent()) {
        return;
    }

    // Select one of the cards
    if (!mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    // Show card UID on LCD
    lcd.setCursor(0, 0); // Set the cursor to column 0, row 0
    lcd.print("Card UID:");

    // Clear the second line before printing the new UID
    lcd.setCursor(0, 1);
    lcd.print("                ");
    lcd.setCursor(0, 1);

    // Print UID
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        if(mfrc522.uid.uidByte[i] < 0x10) {
            lcd.print("0");
            Serial.print("0"); // Print "0" to the serial console if needed
        }
        lcd.print(mfrc522.uid.uidByte[i], HEX);
        Serial.print(mfrc522.uid.uidByte[i], HEX); // Print the UID to the serial console
    }
    Serial.println(); // Move to a new line on the serial console after printing the UID

    // Halt PICC
    mfrc522.PICC_HaltA();
    // Stop encryption on PCD
    mfrc522.PCD_StopCrypto1();
}
