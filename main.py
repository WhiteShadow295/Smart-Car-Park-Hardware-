import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pyrebase import pyrebase
from time import sleep
from datetime import datetime, date
from grove.display.grove_lcd import *
from dotenv import load_dotenv
import os

GPIO.setwarnings(False)
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

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(os.getenv('EMAIL'), os.getenv('PASSWORD'))
db = firebase.database()

## Motor
# Set GPIO mode to BCM
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

# Setup for Servo Motor
GPIO.setup(12, GPIO.OUT)   # Use BCM pin number
p = GPIO.PWM(12, 50)

p.start(0)                 # Initialize PWM with a duty cycle of 0%

def main():
    try:
        while True:
            
            print("run")
            
            isitFull = checkRemainingSlot()
            
            if isitFull == True:
                setText('Car Park Full')
                sleep(2)
            
            else:
                setText("Place your tag")
                iden, text = reader.read()
                print(iden)
                    
                registered_ids = db.child("carpark_history").get(user['idToken'])
               
                found = False
                car_id = ""
                
                for rfid in registered_ids.each():
                    if str(rfid.val()['rfid_id']) == str(iden):
                        car_id = rfid.key()
                        username = rfid.val()['rfid_username']
                        found = True
                        break

                if found == True:  
                    setText("Welcome " + username + "!")
                    p.ChangeDutyCycle(10.5)  # Move servo to 90 degrees
                    print("Open")
                        
                    sleep(2)
                    p.ChangeDutyCycle(6.3)  # Ensure servo is at 0 degrees
                    print("Close")
                        
                    sleep(1)
                        
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print("Enter time: ", time)
                    
                    path = f'carpark_history/{car_id}/checkInOutRecords'    
                          
                    db.child(path).push({
                                "checkInTime" : time,
                                "checkOutTime" : ""
                                })
                    
                    print("Upload Successfully")
                        
                else:
                    setText("Unauthorised    Access")
                    sleep(2)
                        
    except KeyboardInterrupt:
        print("Program ended")
    finally:
        GPIO.cleanup()
        
def checkRemainingSlot():
    ## check the car remaining slot
    carSlotLeft = db.child('Carpark').get()
    carNum = 3

    if carSlotLeft:
        for car in carSlotLeft.each():
            if car.val() == False:
                carNum = carNum - 1
    
    if carNum == 0:
        return True
    else:
        return False
        
if __name__ == "__main__":
    main()
