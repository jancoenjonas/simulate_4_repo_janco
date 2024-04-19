#include <WiFi.h>
#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);  // Adjust these pins as needed
const char* ssid = "WIFI_SSID";
const char* password = "WIFI_PASSWORD";
const char* host = "firebeetle_ip";  
const int port = 80;

void setup() {
    Serial.begin(115200);
    lcd.begin(16, 2);
    lcd.print("Connecting...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        lcd.print(".");
    }
    lcd.clear();
    lcd.print("Connected!");
}

void loop() {
    WiFiClient client;
    if (!client.connect(host, port)) {
        lcd.clear();
        lcd.print("Server conn failed");
        delay(1000);
        return;
    }
    
    String line = client.readStringUntil('\n');
    if (line.length() > 0) {
        lcd.clear();
        lcd.print(line);
    }
    client.stop();
    delay(1000); // Delay between updates
}
