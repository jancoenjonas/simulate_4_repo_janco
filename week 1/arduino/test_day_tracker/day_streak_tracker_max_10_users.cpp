#include <SPI.h>
#include <MFRC522.h>
#include <EEPROM.h>

#define SS_PIN    D5  // Adjust to your ESP32's SPI pin
#define RST_PIN   D6  // Adjust to your ESP32's reset pin for RFID
#define EEPROM_SIZE 512 // Allocate enough space for EEPROM

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance

struct UserData {
    String id;
    int currentStreak;
    int longestStreak;
    long lastScanTime;
};

UserData users[10]; // Array to store data for up to 10 users
const char* SEPARATOR = "|"; // Separator character for serialization

// Function prototypes
void loadUserData();
void handleNewScan(String id);
UserData* findUserById(String id);
void updateStreak(UserData& user);
void saveUserData();
String serializeUserData(const UserData& user);
UserData deserializeUserData(const String& data);

void setup() {
    Serial.begin(9600);
    SPI.begin();
    mfrc522.PCD_Init();

    EEPROM.begin(EEPROM_SIZE);
    loadUserData(); // Load user data from EEPROM
}

void loop() {
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
        String readID = "";
        for (byte i = 0; i < mfrc522.uid.size; i++) {
            readID += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
            readID += String(mfrc522.uid.uidByte[i], HEX);
        }
        readID.toUpperCase();
        handleNewScan(readID);
        mfrc522.PICC_HaltA();
    }
}

void handleNewScan(String id) {
    UserData* user = findUserById(id);
    if (user != nullptr) {
        updateStreak(*user);
        saveUserData();
        Serial.println("ID: " + user->id + " Streak: " + String(user->currentStreak) + " Longest: " + String(user->longestStreak));
    } else {
        Serial.println("Unknown ID");
    }
}

UserData* findUserById(String id) {
    for (int i = 0; i < 10; i++) {
        if (users[i].id == id) {
            return &users[i];
        }
    }
    return nullptr;
}

void updateStreak(UserData& user) {
    long currentTime = millis();
    //24 hours
    if (currentTime - user.lastScanTime >= 86400000) { 
        if (currentTime - user.lastScanTime < 2 * 86400000) {
            user.currentStreak++;
        } else {
            user.currentStreak = 1;
        }
        if (user.currentStreak > user.longestStreak) {
            user.longestStreak = user.currentStreak;
        }
        user.lastScanTime = currentTime;
    }
}

String serializeUserData(const UserData& user) {
    return user.id + SEPARATOR + 
           String(user.currentStreak) + SEPARATOR + 
           String(user.longestStreak) + SEPARATOR + 
           String(user.lastScanTime);
}

UserData deserializeUserData(const String& data) {
    UserData user;
    int sep1 = data.indexOf(SEPARATOR);
    int sep2 = data.indexOf(SEPARATOR, sep1 + 1);
    int sep3 = data.indexOf(SEPARATOR, sep2 + 1);

    user.id = data.substring(0, sep1);
    user.currentStreak = data.substring(sep1 + 1, sep2).toInt();
    user.longestStreak = data.substring(sep2 + 1, sep3).toInt();
    user.lastScanTime = data.substring(sep3 + 1).toInt();

    return user;
}

void loadUserData() {
    if (EEPROM.read(0) == '#') { // Check if data is stored
        String eepromData = "";
        for (int i = 1; i < EEPROM_SIZE; i++) {
            char ch = EEPROM.read(i);
            if (ch == '\0') break;
            eepromData += ch;
        }

        int prevIndex = 0, nextIndex;
        for (int i = 0; i < 10; i++) {
            nextIndex = eepromData.indexOf('\n', prevIndex);
            if (nextIndex == -1) break;
            String userDataStr = eepromData.substring(prevIndex, nextIndex);
            users[i] = deserializeUserData(userDataStr);
            prevIndex = nextIndex + 1;
        }
    }
}

void saveUserData() {
    EEPROM.write(0, '#'); // Mark that data is stored
    int eepromIndex = 1;
    for (int i = 0; i < 10; i++) {
        String userDataStr = serializeUserData(users[i]) + "\n";
        for (int j = 0; j < userDataStr.length(); j++) {
            EEPROM.write(eepromIndex++, userDataStr[j]);
        }
    }
    EEPROM.commit();
}
