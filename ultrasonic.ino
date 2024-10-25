#include <WiFi.h>
#include <Firebase_ESP_Client.h>

#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

// WiFi credentials
#define wifi_ssid "YOUR_WIFI_SSID"
#define wifi_password "YOUR_WIFI_PASSWORD"

#define API_KEY "YOUR_API_KEY"
#define DATABASE_URL "YOUR_DATABASE_URL"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Ultrasonic sensor pins
const int ULTRASONIC_TRIG_PIN[] = {23, 19, 26, 34};
const int ULTRASONIC_ECHO_PIN[] = {22, 21, 27, 35};
const float DISTANCE_THRESHOLD = 5.0;  // Distance threshold in cm

void setup_wifi(){
  delay(10);
  WiFi.begin(wifi_ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED){
    Serial.println("WiFi reconnecting...");
    delay(500);
  }
  Serial.println("WiFi connected.");
}

void initializeFirebase() {
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("ok");
  } else {
    Serial.printf("Error 404");
    Serial.printf("%s\n", config.signer.signupError.message.c_str());
  }

  Serial.println("ok1");
  config.token_status_callback = tokenStatusCallback; // Assign the callback function for the long running token generation task, see addons/TokenHelper.h
  Serial.println("ok2");

 // here got error
  Firebase.begin(&config, &auth);
  Serial.println("ok3");
  Firebase.reconnectWiFi(true);
  Serial.println("ok4");
}

void setup(){
  Serial.begin(115200);
  setup_wifi();
  initializeFirebase();
  for(int i = 0; i < 4; i++){
    pinMode(ULTRASONIC_TRIG_PIN[i], OUTPUT);
    pinMode(ULTRASONIC_ECHO_PIN[i], INPUT);
  }
 
}

void readUltrasonic(){
  float duration_us[4], distance_cm[4];
  String slot[] = {"Slot_1", "Slot_2", "Slot_3", "Slot_4"};
  
  // Get distance for each slot
  for (int i = 0; i < 4; i++){
    digitalWrite(ULTRASONIC_TRIG_PIN[i], HIGH);  
    delayMicroseconds(10);
    digitalWrite(ULTRASONIC_TRIG_PIN[i], LOW);

    duration_us[i] = pulseIn(ULTRASONIC_ECHO_PIN[i], HIGH); 
    distance_cm[i] = 0.017 * duration_us[i];

    Serial.print(i+1);
    Serial.print(". distance: ");
    Serial.print(distance_cm[i]);
    Serial.println(" cm");

    String path = "/Carpark/" + slot[i]; 
    if (distance_cm[i] >= DISTANCE_THRESHOLD){

     Firebase.RTDB.setBool(&fbdo, path, true);
     Serial.println("True");
     
    } else {
      
      Firebase.RTDB.setBool(&fbdo, path, false);
      Serial.println("False");
    }
  }
}

void loop(){
  readUltrasonic();
  delay(2500); // Delay of 2.5 second between reads
}
