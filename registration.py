import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pyrebase import pyrebase
from time import sleep
from dotenv import load_dotenv
import os

reader = SimpleMFRC522()

# Load environment variables from .env file
load_dotenv()

firebaseConfig = {
  "apiKey": os.getenv('API_KEY'),
  "authDomain": os.getenv('AUTH_DOMAIN'),
  "databaseURL": os.getenv('DATABASE_URL'),
  "projectId": os.getenv('PROJECT_ID'),
  "storageBucket": os.getenv('STORAGE_BUCKET'),
  "messagingSenderId": os.getenv('MESSAGING_SENDER_ID'),
  "appId": os.getenv('APP_ID'),
  "measurementId": os.getenv('MEASUREMENT_ID')
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(os.getenv('EMAIL'), os.getenv('PASSWORD'))
db = firebase.database()

try:
    while True:
        print("Place the tag to register")
        iden, text = reader.read()
        print("RFID ID: ", iden)
        print("RFID Text: ", text)
        
        # Ask for username or other information for registration
        username = input("Enter username associated with this RFID: ")
        
        # Structure the data
        data = {
            "rfid_id": iden,
            "rfid_username": username,
            "checkInOutRecords": []
        }
        
        # Store the data in Firebase under the 'registered_rfids' node
        results = db.child("carpark_history").push(data, user['idToken'])
        print("RFID registered successfully.")
        
        # Option to break the loop if you don't want to keep registering RFIDs
        cont = input("Do you want to register another RFID? (yes/no): ")
        if cont.lower() != 'yes':
            break
        
        sleep(1)
        
except KeyboardInterrupt:
    print("Registration process interrupted.")
finally:
    GPIO.cleanup()