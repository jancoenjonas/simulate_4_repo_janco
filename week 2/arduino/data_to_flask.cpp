#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include "secret.h" 

#define RST_PIN 26 
#define SS_PIN 25  

MFRC522 mfrc522(SS_PIN, RST_PIN); 

void sendDataToFlaskServer(const char* data) {
  WiFiClient client;
  if (!client.connect(SECRET_FLASK_SERVER, SECRET_FLASK_PORT)) {
    Serial.println("Connection to Flask server failed");
    return;
  }
  
  String url = "/upload-data";
  url += "?data=";
  url += data;

  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + SECRET_FLASK_SERVER + "\r\n" +
               "Connection: close\r\n\r\n");

  delay(10);
  client.stop();
}

void setup() {
  Serial.begin(115200);
  SPI.begin(); 
  mfrc522.PCD_Init(); 

  WiFi.begin(SECRET_SSID, SECRET_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String content = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
      content.concat(String(mfrc522.uid.uidByte[i], HEX));
    }

    Serial.print("NFC UID:");
    Serial.println(content);
    sendDataToFlaskServer(content.c_str());
  }
  delay(1000); // Adjust delay as needed
}
