import RPi.GPIO as GPIO

import cv2

import numpy as np

import os

import time 

 

GPIO.setmode(GPIO.BCM)

PIR_PIN = 17 # OUT pin number

GPIO.setup(PIR_PIN, GPIO.IN)

 

 

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.read('trainer/trainer.yml')

cascadePath = "haarcascades/haarcascade_frontalface_default.xml"

faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

 

#iniciate id counter

id = 0

# names related to ids: example ==> loze: id=1,  etc

# 이런식으로 사용자의 이름을 사용자 수만큼 추가해준다.

names = ['None', 'jeongmin', 'ljy', 'chs', 'ksw']     #id =0 이고 테스트할때 입>

 

# Initialize and start realtime video capture

cam = cv2.VideoCapture(0)

cam.set(3, 640) # set video widht

cam.set(4, 480) # set video height

 

# Define min window size to be recognized as a face

minW = 0.1*cam.get(3)

minH = 0.1*cam.get(4)

try:

    time.sleep(2)

    print("motion search")

    while True:

        if GPIO.input(PIR_PIN):

           t = time.localtime()

            ret, img =cam.read()
            img = cv2.flip(img, 1) # 화면 반전 1 or -1

            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
            faces = faceCascade.detectMultiScale(gray,scaleFactor = 1.2,
                    minNeighbors = 6,
                    minSize = (int(minW), int(minH)),)

            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
               # Check if confidence is less them 100 ==> "0" is perfect match
                if (confidence > 45):  #카메라 인식하고 학습된 데이터와 연관성[>
                    id = names[id]
                    confidence = "  {0}%".format(round(100 - confidence))
                else:                   #얼굴은 인식했지만 데이터와 연관성이 없>
                    id = "unknown"
                    confidence = "  {0}%".format(round(100 - confidence))

                cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)>
                cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,25>
    
            cv2.imshow('camera',img) # 화면에 카메라 띄움
            k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break

    # Do a bit of cleanup
except KeyboardInterrupt:
    print (" quit")
    GPIO.cleanup()
cam.release()
cv2.destroyAllWindows()
