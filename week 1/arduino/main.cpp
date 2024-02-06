#include <WiFi.h>
#include <WebServer.h>
#include <SPI.h>
#include <MFRC522.h>
#include "secret.h" 

#define RST_PIN 26 
#define SS_PIN 25  

MFRC522 mfrc522(SS_PIN, RST_PIN); 
WebServer server(80);

// HTML voor de loginpagina
const char* loginPageHTML = 
  "<html>"
  "<head><title>Login</title></head>"
  "<body>"
  "<form action='/login' method='POST'>"
  "Gebruikersnaam: <input type='text' name='username'><br>"
  "Wachtwoord: <input type='password' name='password'><br>"
  "<input type='submit' value='Inloggen'>"
  "</form>"
  "</body>"
  "</html>";

// HTML voor de NFC-data pagina
const char* nfcDataPageHTML = 
  "<html>"
  "<head><title>NFC Data</title></head>"
  "<body>"
  "<h1>Welkom, janco!</h1>"
  "<p>NFC UID: 4A 5B 6C 7D</p>" // Dummy NFC UID
  "</body>"
  "</html>";

void handleRoot() {
  server.send(200, "text/html", loginPageHTML);
}

void handleLogin() {
  if (server.hasArg("username") && server.hasArg("password")) {
    if (server.arg("username") == "janco" && server.arg("password") == "iot") {
      server.send(200, "text/html", nfcDataPageHTML);
    } else {
      server.send(200, "text/html", "<p>Login mislukt. Probeer opnieuw. Ga terug naar <a href='/'>login</a>.</p>");
    }
  } else {
    server.send(400, "text/html", "<p>Verkeerde aanvraag. Ga terug naar <a href='/'>login</a>.</p>");
  }
}

void handleNFCData() {
  // Dummy NFC data
  server.send(200, "text/html", nfcDataPageHTML);
}

void setup() {
  Serial.begin(115200);
  SPI.begin(); // Initieer SPI bus
  mfrc522.PCD_Init(); // Initieer MFRC522
  Serial.println("RFID reading UID");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi verbonden.");

  server.on("/", handleRoot);
  server.on("/login", handleLogin);
  server.on("/nfc-data", handleNFCData);
  server.begin();
  Serial.println("HTTP server gestart");
}

void loop() {
  server.handleClient();
}
