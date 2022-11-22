# face_recog.py

import face_recognition
import cv2
import os
import numpy as np
import time
import socket
import select
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials, initialize_app, storage
        
class FaceRecog():

    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        
        #초기 변수 설정
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.flag = 1
        self.timecheck = 0
        self.start = 0
        self.end = 0
        self.i = 0
        self.default = './default.mp4'
        self.video = cv2.VideoCapture(self.default)
        self.sFlag = True
        self.upload = "./upload/"
        self.upload2 = "./upload2/"
        self.user = "./user/"
        self.end3 = "./end3/"
        self.k = len(os.listdir(self.end3)) +1
        self.PORT = 6666
        self.num = 0

        self.cred = credentials.Certificate("/home/serv/Desktop/myreactnative-a5066-firebase-adminsdk-131ka-2938baa8b2.json")
        firebase_admin.initialize_app(self.cred,{ 'databaseURL' : 'https://myreactnative-a5066-default-rtdb.firebaseio.com/', 'storageBucket' : f'myreactnative-a5066.appspot.com'})

        self.surl = "gs://myreactnative-a5066.appspot.com/image_store/" # storage url
        self.dir = db.reference()#기본 위치 지정
        self.ref = db.reference()
        self.bucket = storage.bucket()
        
        
        
        #사용자의 id번호로 2차원 배열 필드를 만들어 가장 정확도가 높은 사람의 id를 출력

        self.f_recog = [[0 for j in range(50)] for i in range(2)]

    def __del__(self):
        try:
            self.video.release()
            print("비디오 종료")
            self.s_sock.close()
            print("socket 종료")
        except:
            print(" ")
        del self.video

    def userrenew(self, flag):
        # 사용자를 등록하는 함수 
        if flag == 1:
            imagepath = self.upload
            print("새로 업로드된 유저를 업데이트합니다.")
        else:
            imagepath = self.user
        
        files = os.listdir(imagepath)
        if not files:
            print("등록할 파일이 없습니다!!! 재실행 요망")
        for filename in files:
            name, ext = os.path.splitext(filename) #파일 이름 , 확장자
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(imagepath, filename)
                img = face_recognition.load_image_file(pathname)    #인식기에 사진추가
                try:
                    face_encoding = face_recognition.face_encodings(img)[0] #인식기 인코딩
                except:
                    print(filename + "이 파일은 Dlib에서 인식하지 못하므로 삭제하시면 됩니다")
                self.known_face_encodings.append(face_encoding) #인코딩값 추가
                if flag == 1:
                    os.system('mv ' + self.upload + filename+ ' '+ self.user)

        



    def socketconnect(self):
        IP = ''
        self.sockmsg = ''
        s_addr = (IP, self.PORT)
        self.s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_sock.bind(s_addr)
        self.s_sock.listen()

         #self.readsock = [self.s_sock]
            

        print("클라이언트 연결 대기중")
        self.c_sock, self.c_addr = self.s_sock.accept()
        #readsock.append(self.c_sock)
        print( str(self.c_addr) + " 클라이언트 접속")

        self.sendmsg("서버와 연결되었습니다")
        self.recvmsg()


    def sendmsg(self, msg):
        self.c_sock.send(msg.encode())

    def recvmsg(self):
        while True:
            msg = self.c_sock.recv(1024)
            if msg is not None:
                break
        msg = msg.decode('utf-8')
        print("cli: " + msg)
        self.sockmsg = msg
        self.msgcheck()

    def msgcheck(self):
        if self.sockmsg == "1":
            self.userrenew(1)
            self.recvmsg()
            self.sockmsg =""


    def get_cframe(self):
        ret, frame = self.video.read()

        return frame

    def get_frame(self):

        if self.i == 3:
            self.i = 0
            self.flag = 1
            namevalue = "-01"
            maxindex = self.f_recog[1].index(max(self.f_recog[1]))
            
            if maxindex == 0:
                namevalue = "-00"
                self.sendmsg("인가되지 않은 사용자 입니다.")
            
            else:
                self.sendmsg("인가된 사용자 입니다.")
            
            mvideo = self.nowvideo.rstrip(".mp4") + namevalue + ".mp4"
            os.system('mv ' + self.nowvideo + " ./"+ mvideo)
            nvideo = os.listdir(self.upload2)[0]
            
            try:
                blob = self.bucket.blob('image_store/' + nvideo)
                blob.upload_from_filename(filename = mvideo, content_type = 'mp4')
                print("mp4 file spend")
            except:
                print("storage upload error!")


            try:
                self.ref = db.reference('DB/{0}'.format(self.k))
                self.ref.update({'num':self.k})
                self.ref.update({'date':nvideo})
                self.ref.update({'URL': self.surl + nvideo})

                if maxindex == 0:
                    self.ref.update({'category':"unknown"})
                    print("unknown upload db")
                    
                else:
                    self.ref.update({'category':"known"})
                    print("known upload db")
                    
                self.k = self.k + 1
            except:
                print("파이어베이스db 업로드에 오류발생")



            self.f_recog[1] = [0 for i in range(50)]
            os.system('mv ' + mvideo + " " + self.end3)




        if self.flag == 1:
            self.start = time.time()
            self.flag=2
            self.t = 0
            print("flag start")

            try:
                self.recvmsg()
                self.nowvideo = self.upload2 + os.listdir(self.upload2)[0]
                self.video = cv2.VideoCapture(self.nowvideo)
            except:
                print("파일이 없음!!!")
                time.sleep(1)
                return

            

        self.end = time.time()
        self.timecheck = self.end - self.start

        if self.timecheck > 1.0:
            self.video = cv2.VideoCapture(self.nowvideo)
            
            self.start = time.time()
            self.i = self.i + 1
            time.sleep(0.01)

        #print("timecheck : " + str(self.timecheck))


        #비디오에서 프레임을 뽑아옴
        frame = self.get_cframe()
        #print("check")
        
        # 비디오 프레임을 1/4 사이즈로 리사이즈함 (속도 개선, face_rcogniton에 적합하게)
        try:           
            small_frame = cv2.resize(frame, None, fx=0.25, fy=0.25, interpolation = cv2.INTER_AREA)
        except: #프레임 따오는도중 오류가 생길 수 있음 현재 영상을 다시 불러온 후 다시 프레임 탐색
            print("error try get frame")
            small_frame = self.error_except_loop()


        # 이미지를  BGR에서 (OpenCV가 사용함) RGB로 변경 (face_recognition 가 사용)
        rgb_small_frame = small_frame[:, :, ::-1]

        # 비디오 한 프레임마다 처리함
        if self.process_this_frame:
            self.face_locations = face_recognition.face_locations(rgb_small_frame) # 얼굴영역 찾기
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations) #face 인코딩 계산

            self.face_names = []
            for face_encoding in self.face_encodings:
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding) #인코딩값 유사도 비교
                min_value = min(distances) 
                #유클리드 거리로 계산한 값이 유사도 이 값이 0~1, 0에 가까울수록 동일함
                # 내부 태스트결고 0.4이 가장 효율적이었음
                name = "Unknown"
                if min_value < 0.4:
                    index = np.argmin(distances)    #배열 마지막에 가장 유사한 사람의 index가 적혀짐 min_value에서 걸러지거나 index = -1 일때  unknown
                    name = self.known_face_names[index]

                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame

        # 결과 표시
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # 얼굴영역 사각형으로 표시
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # 사각형 아래에 이름을 쓸 공간 확보
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            if(name !="Unknown"):
                fid = name.split("_")[1]
                fname = name.split("_")[2]
                self.f_recog[1][int(fid)] = self.f_recog[1][int(fid)] + 1
            else:
                fname = "Unknown"
                self.f_recog[1][0] = self.f_recog[1][0] + 1

            #식별한 이름 표시
            cv2.putText(frame, fname, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            #name.split("_")[2] 에서 토큰 _ id =1, name= 2





        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()

    def default_mp4(self):
        self.video = cv2.VideoCapture(self.default)

    def error_except_loop(self):
        result = "" 
        while(True):
            try:
                time.sleep(0.1)
                frame = self.get_cframe()
                result = cv2.resize(frame, None, fx=0.25, fy=0.25, interpolation = cv2.INTER_AREA)
                return result
            except:
                self.video = cv2.VideoCapture(self.nowvideo)
                time.sleep(0.6)
                continue

        return result

if __name__ == '__main__':
    print(" 사용자 등록 및 초기설정중...")
    face_recog = FaceRecog()
    face_recog.userrenew(0)
    print("설정 완료!")
    face_recog.socketconnect()

    while True:
        frame = face_recog.get_frame()

        # show the frame
        try:
            cv2.imshow("Frame", frame)
        except:
            pass
        key = cv2.waitKey(1) & 0xFF

        # q 누르면 종료
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()

    print('finish')
     
