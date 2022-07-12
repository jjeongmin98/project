import cv2
import os
import firebase_admin
import time 
import RPi.GPIO as GPIO
from firebase_admin import credentials
from firebase_admin import storage
from uuid import uuid4

GPIO.setmode(GPIO.BCM)
PIR_PIN = 17 # OUT pin number

GPIO.setup(PIR_PIN, GPIO.IN)

PROJECT_ID = "project-3eb4c"
#my project id
cred = credentials.Certificate("/home/ubuntu/다운로드/project-3eb4c-firebase-adminsdk-29sv1-229127f941.json") #(키 이름 ) 부분에 본인의 키이름을 적어주세요.
default_app = firebase_admin.initialize_app(cred,{'storageBucket':f"{PROJECT_ID}.appspot.com"})
#버킷은 바이너리 객체의 상위 컨테이너이다. 버킷은 Storage에서 데이터를 보관하는 기본 컨테이너이다.
bucket = storage.bucket()#기본 버킷 사용

def fileUpload(file):
    blob = bucket.blob('image_store/'+file) #저장한 사진을 파이어베이스 storage의 image_store라는 이름의 디렉토리에 저장
    #new token and metadata 설정
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token} #access token이 필요하다.
    blob.metadata = metadata
    #upload file
    blob.upload_from_filename(filename='/home/ubuntu/pj/dataset/'+file, content_type='image/jpg') #파일이 저장된 주소와 이미지 형식(jpeg도 됨)
    #debugging hello
    print("hello ")



cam = cv2.VideoCapture(0)  #캠 디바이스 아이디 0이면 기본값
cam.set(3, 640) # set video width 좌측 인자가 width 우측인자가 크기
cam.set(4, 480) # set video height
face_detector = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml') #얼굴 인식할 기본 베이스 api

# For each person, enter one numeric face id
face_id = input('\n enter user id end press <return> ==>  ')  #얼굴인식할 사람의 id를 입력받음
print("\n [INFO] Initializing face capture. Look the camera and wait ...")

# Initialize individual sampling face count
count = 0
try:
    while(True):
        if GPIO.input(PIR_PIN):
            t = time.localtime()
            print (" %d:%d:%d motion detected!" % (t.tm_hour, t.tm_min, t.tm_sec))
            ret, img = cam.read()   #카메라 읽기
            #img = cv2.flip(img, -1) # 상하반전 -1 or 1
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                count += 1  #반복문 카운트
            # Save the captured image into the datasets folder
                cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])  #dataset/user.사용자id.표본번호.jp
                cv2.imshow('image', img)    #인식할때 화면 보여줌

                filename = "User." + str(face_id) + '.' + str(count) + ".jpg"
                fileUpload(filename)

            k = cv2.waitKey(100) & 0xff #  'ESC' 누르면 취소
            if k == 27:
                break
            elif count >= 5: # 얼굴인식 러닝을 위해 사진을 찍을 표본수 #30장
                break
        time.sleep(0.05)
except KeyboardInterrupt:
    print (" quit")
    GPIO.cleanup()
#filename = "User." + str(face_id) + '.' + str(n) + ".jpg"
#fileUpload(filename)

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
