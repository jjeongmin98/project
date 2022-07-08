import cv2
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from uuid import uuid4

PROJECT_ID = "project-3eb4c"
#my project id
 
cred = credentials.Certificate("/home/ubuntu/다운로드/project-3eb4c-firebase-adminsdk-29sv1-229127f941.json") #(키 이[>
default_app = firebase_admin.initialize_app(cred,{'storageBucket':f"{PROJECT_ID}.appspot.com"})
#버킷은 바이너리 객체의 상위 컨테이너이다. 버킷은 Storage에서 데이터를 보관하는 기본 컨테이너이다.
bucket = storage.bucket()#기본 버킷 사용

def fileUpload(file):
    blob = bucket.blob('image_store/'+file) #저장한 사진을 파이어베이스 storage의 image_store라는 이름의 디렉토리에 저>
    #new token and metadata 설정
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token} #access token이 필요하다.
    blob.metadata = metadata
 
    #upload file
    blob.upload_from_filename(filename='/home/ubuntu/pj/dataset/'+file, content_type='image/jpg') #파일이 저장된 주소[>
    #debugging hello
    print("hello ")


cam = cv2.VideoCapture(0)  #캠 디바이스 아이디 0이면 기본값
#cv2.VideoCapture : 장치관리자에 등록되어 있는 카메라 순서대로 인덱스 설정되어있다.
cam.set(3, 640) # set video width 좌측 인자가 width 우측인자가 크기
cam.set(4, 480) # set video height
face_detector = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml') #얼굴 인식할 기본 베이스 api
#Harr-Cascade : 트레이닝 데이터를 각각 읽어 CascadeClassifier 객체를 생성한다.

# For each person, enter one numeric face id
face_id = input('\n enter user id end press <return> ==>  ')  #얼굴인식할 사람의 id를 입력받음
print("\n [INFO] Initializing face capture. Look the camera and wait ...")

# Initialize individual sampling face count
count = 0
while(True):
    ret, img = cam.read()   #카메라 읽기
    #img = cv2.flip(img, -1) # 상하반전 -1 or 1
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
    #gray의 얼굴을 검출한다. 얼굴이 검출되면 위치를 리스트로 리턴한다. 위치는 (x,y,w,h)와 같은 튜플이며 
    #는(x,y)는 검출된 얼굴의 좌상단 위치, w,h는 가로 세로크기이다.
    #gray 뒤에 값 1.3은 scaleFactor, 5는 minNeighbor을 의미한다.
    #이때 scaleFactor은 이미지 스케일에서 이미지 크기를 줄이는 방법을 지정하는 매개 변수이다. 크기를 줄여서 발견될 가능성을 높이는 것을 의미한다
    #minNeighbors 는 각 후보 사각형이 유재히야하는 이웃수를 지정하는 매개변수이며, 이때 값이 클수록 덜 감지되지만 품질이 높아진다.
    filename = "User." + str(face_id) + '.' + str(count) + ".jpg"
    fileUpload(filename)

    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1  #반복문 카운트
        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])  #dataset/user.사용자id.표본번호.jpg
        cv2.imshow('image', img)    #인식할때 화면 보여줌
    k = cv2.waitKey(100) & 0xff #  'ESC' 누르면 취소
    if k == 27:
         break
    elif count >= 30: # 얼굴인식 러닝을 위해 사진을 찍을 표본수 #30장
         break
# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
