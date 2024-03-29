# face_recog.py

import face_recognition
import cv2
import os
import numpy as np

class FaceRecog():
    def __del__(self):
        self.video.release()

    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture('/home/serv/Desktop/video.mp4')

        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize it.
        dirname = 'upload'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename) #파일 이름 , 확장자
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)    #인식기에 사진추가
                try:
                    face_encoding = face_recognition.face_encodings(img)[0] #인식기 인코딩
                except:
                    print(filename)
                self.known_face_encodings.append(face_encoding) #인코딩값 추가

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
  
#    def __del__(self):
#        del self.camera

    def get_frame(self):
        # Grab a single frame of video
        ret,frame = self.video.read()
        
        # Resize frame of video to 1/4 size for faster face recognition processing
        
        small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:# 비디오 프레임 처리
            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame) # 얼굴영역 찾기
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations) #face 인코딩 계산

            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding) #인코딩값 유사도 비교
                min_value = min(distances) #유클리드 거리로 계산한 값이 유사도 이 값이 0~1, 0에 가까울수록 동일함

                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.
                name = "Unknown"
                if min_value < 0.4:
                    index = np.argmin(distances)    #배열 마지막에 가장 유사한 사람의 index가 적혀짐 min_value에서 걸러지거나 index = -1 일때  unknown
                    name = self.known_face_names[index]

                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            if(name !="Unknown"):
                fname = name.split("_")[2]
            else:
                fname = "Unknown"

            cv2.putText(frame, fname, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            #name.split("_")[2] 에서 토큰 _ id =1, name= 2

        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()


if __name__ == '__main__':
    face_recog = FaceRecog()
    print(face_recog.known_face_names)
    while True:
        frame = face_recog.get_frame()

        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')
