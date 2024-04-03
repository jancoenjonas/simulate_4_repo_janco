#include <SPI.h>
#include <MFRC522.h>
#include "Wire.h"
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define RST_PIN 26
#define SS_PIN  SDA



// Initialize the RFID reader
MFRC522 mfrc522(SS_PIN, RST_PIN); 

// Set the LCD address for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
    Serial.begin(115200); // Initialize serial communications with the PC
    SPI.begin();          // Init SPI bus
    mfrc522.PCD_Init();   // Init MFRC522 card
    lcd.init();           // Initialize the LCD
    lcd.backlight();      // Turn on the backlight

    // Connect to WiFi
    lcd.clear();
    lcd.print("WiFi romance in");
    lcd.setCursor(0, 1); // Move cursor to the second line
    lcd.print("de maak...💘");

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    // Display WiFi connection success message
    lcd.clear();
    lcd.print("Match gevonden!");
    lcd.setCursor(0, 1);
    lcd.print("WiFi ❤️ ESP32");

    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.println("RFID reader initialized. Waiting for NFC tag...");
}

void loop() {
    // Display message indicating the device is waiting for a tag
    lcd.clear();
    lcd.print("Lonely NFC zoekt");
    lcd.setCursor(0, 1);
    lcd.print("badge 🥺🔍");

    // Look for new RFID cards
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        delay(50); // Wait a bit before trying again
        return;
    }

    // Display NFC tag detected message
    lcd.clear();
    lcd.print("Badge gespot! 🎯");
    lcd.setCursor(0, 1);
    lcd.print("Bingo! Winnaar.");

    // Convert UID to a string
    String uidString = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        uidString += String(mfrc522.uid.uidByte[i], HEX);
    }

    // Send UID to the server
    sendTagToServer(uidString);

    // Halt PICC and stop encryption on PCD
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();

    delay(2000); // Wait a bit before reading again to allow the user to read the LCD
}

void sendTagToServer(String uid) {
    if(WiFi.status()== WL_CONNECTED){   //Check WiFi connection status
        HTTPClient http;    //Declare an object of class HTTPClient
        http.begin("https://attendance-kdg.com/nfc");      //Specify request destination
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");  //Specify content-type header

        // This sends a post request to the server with the UID
        // You might need to adjust the data format depending on your server's requirements
        int httpResponseCode = http.POST("uid=" + uid);

        if(httpResponseCode>0){
            String response = http.getString();                       //Get the response to the request
            Serial.println(httpResponseCode);   //Print return code
            Serial.println(response);           //Print request answer
        }else{
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }

        http.end();  //Close connection
    }else{
        Serial.println("Error in WiFi connection");
    }
}
