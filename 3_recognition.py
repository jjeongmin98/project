import RPi.GPIO as GPIO
import cv2
import numpy as np
import os
import time 

GPIO.setmode(GPIO.BCM)
PIR_PIN = 17 # OUT pin number
GPIO.setup(PIR_PIN, GPIO.IN)

now = time
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX
unknown , a = 0
 
def speak(option, msg) :
    os.system("espeak {} '{}'".format(option,msg))
    

#iniciate id counter
id = 0
# names related to ids: example ==> loze: id=1,  etc
# 이런식으로 사용자의 이름을 사용자 수만큼 추가해준다.
newname = [100]
names = ['None', 'jeongmin', 'ljy', 'chs', 'ksw']    #id =0 이고 테스트할때 입력한 id를 1로 입력해 놓아서 2번째(names[1])에 이름설정했음
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
    print("현재시간 : ", now.strftime('%Y-%m-%d %H:%M:%S'))
    #모듈에서 인식될경우
    f = open('log.txt', 'w')
    f.write(now.strftime('%Y-%m-%d %H:%M:%S'))
    f.close()
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
                if (confidence > 45):  #카메라 인식하고 학습된 데이터와 연관성이 보이면 작동
                    id = names[id]
                    confidence = "  {0}%".format(round(100 - confidence))
                    #수정중인 코드!!!
                    if(a==0 and (id not in newname)):
                        newname[a] = names[id]
                        option = '-s 160 -p 95 -a 200 -v ko+f3'
                        #-s : 분당 단어의 속도, -p pitch , -a : 볼륨  -ko+f3 : 한국어의 3번째 목소리
                        msg = '안녕하세요 ' + newname[a] + '님 반갑습니다.'
                        print('espeak', option, msg)
                        speak(option,msg)
                        a +=1
                        
                    

                else:                   #얼굴은 인식했지만 데이터와 연관성이 없으면 작동(외부인)
                    id = "unknown"
                    #unknown이 발견됬을때 기록을 남김 
                    cv2.imwrite("unknowndataset/User." + now.strftime('%Y-%m-%d %H:%M:%S') +'.' + ".jpg",img)
                    f = open('log.txt', 'w')
                    f.write(now.strftime('%Y-%m-%d %H:%M:%S'))
                    f.close()
                    confidence = "  {0}%".format(round(100 - confidence))

                cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)     #화면에 띄우는 창에 사용자 이름 띄워줌
                cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  #얼마나 일치하는지 값을 보여줌

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
