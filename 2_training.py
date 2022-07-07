import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = 'dataset'    #학습할 사진이 들어가있는 폴더.
recognizer = cv2.face.LBPHFaceRecognizer_create()
#LBP 알고리즘을 사용하여 이진 패턴을 계산한다. 즉 인식을 하는 명령어이다. (밝기에는 영향을 미치지 않는다.)


detector = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml");
#단순 객체를 인식하는것

# function to get the images and label data
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]   #f에 파일 이름 넣은 후 경로와 파일이름을 결합 dataset/filename
    faceSamples=[]
    ids = []
    for imagePath in imagePaths:    #imagePaths에 있는 튜플들 하나씩 다 반복 30장찍었으면 30번
        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        #이미지 파일을 연뒤  conver('L')을 이용하여 gray로 바꿔준다. 여기서 'L'은 8비트 그레이스케일을 의미한다.

        img_numpy = np.array(PIL_img,'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])    #경로애서 파일명만 추출한 후 다시 토큰(".")로 분리하여 배열로 생성
        faces = detector.detectMultiScale(img_numpy)    #배열로 생성한것중 [1]항목이 우리가 설정한 id
        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids
print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)
recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi
# Print the numer of faces trained and end program
print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))

#yaml 은 자바 스크립트 텍스트라고도 한다.
