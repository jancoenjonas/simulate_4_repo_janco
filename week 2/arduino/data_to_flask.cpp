#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include "secret.h"

#define RST_PIN 26 
#define SS_PIN 25  

MFRC522 mfrc522(SS_PIN, RST_PIN); 
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Adjust the I2C address if necessary

void sendDataToFlaskServer(const char* data) {
  WiFiClient client;
  if (!client.connect(SECRET_FLASK_SERVER, SECRET_FLASK_PORT)) {
    Serial.println("Connection to Flask server failed");
    lcd.clear();
    lcd.print("Server Verbinding Mislukt");
    return;
  }
  
  String url = "/upload-data";
  url += "?data=";
  url += data;

  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + SECRET_FLASK_SERVER + "\r\n" +
               "Connection: close\r\n\r\n");

  while(client.connected() || client.available()) {
    if (client.available()) {
      String line = client.readStringUntil('\n');
      if (line == "\r") {
        break;  // Headers received, next line is body
      }
    }
  }

  String response = client.readStringUntil('\n');
  displayUserData(response);

  delay(10);
  client.stop();
}

void displayUserData(const String& data) {
  int firstCommaIndex = data.indexOf(',');
  int secondCommaIndex = data.indexOf(',', firstCommaIndex + 1);

  String streak = data.substring(0, firstCommaIndex);
  String longestStreak = data.substring(firstCommaIndex + 1, secondCommaIndex);
  String name = data.substring(secondCommaIndex + 1);

  lcd.clear();
  lcd.print("Streak: " + streak);
  lcd.setCursor(0, 1); // Move to the second line
  lcd.print("Langste: " + longestStreak);
  // Add additional lines or scrolling if necessary
}

void setup() {
  Serial.begin(115200);
  SPI.begin(); 
  mfrc522.PCD_Init(); 
  lcd.init();
  lcd.backlight();

  WiFi.begin(SECRET_SSID, SECRET_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    lcd.clear();
    lcd.print("Verbinden met WiFi");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  lcd.clear();
  lcd.print("WiFi Verbonden");
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String content = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
      content.concat(String(mfrc522.uid.uidByte[i], HEX));
    }

    Serial.print("NFC UID: ");
    Serial.println(content);
    lcd.clear();
    lcd.print("NFC Gescand");
    sendDataToFlaskServer(content.c_str());
  } else {
    lcd.clear();
    lcd.print("Wachten op NFC");
  }
  delay(1000);
}
