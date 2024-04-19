#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         26
#define SS_PIN          5   // Adjust pin if needed
#define BUZZER_PIN      25
#define GREEN_LED_PIN   22
#define ORANGE_LED_PIN  23
#define RED_LED_PIN     24

const char* ssid     = "WIFI_SSID";
const char* password = "WIFI_PASSWORD";
const char* serverName = "http://YOUR_AZURE_VM_IP:5000/post_tag";  // Azure VM server endpoint
WiFiServer server(80);  

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
    Serial.begin(115200);
    SPI.begin();
    mfrc522.PCD_Init();
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(ORANGE_LED_PIN, OUTPUT);
    pinMode(RED_LED_PIN, OUTPUT);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi connected.");
    server.begin();
}

void loop() {
    WiFiClient client = server.available();   // listen for incoming clients from secondary ESP32

    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
        String tagUID = "";
        for (byte i = 0; i < mfrc522.uid.size; i++) {
            tagUID += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "") + String(mfrc522.uid.uidByte[i], HEX);
        }
        tagUID.toUpperCase();

        sendTagToServer(tagUID);  // Send data to Azure VM
        if (client) {
            client.println(tagUID);  // Send the tag UID to the secondary ESP32
            Serial.println("Tag UID sent to secondary ESP32.");
            client.stop();
        }
        
        // Here you could also control LEDs and buzzer based on received data from Azure VM
        digitalWrite(GREEN_LED_PIN, HIGH);  // Example: Indicate a successful read
        delay(100);                        // Short delay for LED indication
        digitalWrite(GREEN_LED_PIN, LOW);

        mfrc522.PICC_HaltA();
        mfrc522.PCD_StopCrypto1();
    }
}

void sendTagToServer(String tagUID) {
    if(WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverName);
        http.addHeader("Content-Type", "application/json");
        String httpRequestData = "{\"tag_uid\":\"" + tagUID + "\"}";
        int httpResponseCode = http.POST(httpRequestData);
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println(httpResponseCode);
            Serial.println(response);
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    }
    else {
        Serial.println("WiFi Disconnected");
    }
}
