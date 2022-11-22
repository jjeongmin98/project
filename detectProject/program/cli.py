import cv2
import ftplib
import os
import socket
import time
import datetime
import select
from gtts import gTTS
from pydub import AudioSegment


class Facerasp():
    def __init__(self):
        try:
            self.cam = cv2.VideoCapture(0)
        except:
            print("카메라 모듈이 감지되지 않았습니다! 재시도 하겠습니다")
            time.sleep(1)
            self.cam = cv2.VideoCapture(0)

        self.cam.set(3, 640)
        self.cam.set(4, 480)
        self.face_detector = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml') #얼굴 인식할 기본 베이스 api
        self.servip = "127.0.0.1" # server ip 테스트용일땐 루프백, 서버컴퓨터껄로 변경
        self.servport = 6666   #포트 개방해논거에 넣으면됨
        self.ftpip = self.servip # 서버 아이피랑 ftp 주소를 다르게한다면 수정
        self.ftpid = "heo"  #ftp id
        self.ftppass = "123rkdlq"  #ftp password
        self.ftpport = 21
        #FTP는 가능하면 절대경로로
        self.cpath1="/home/heo/openCV/change/lastbuild/dataset/"
        self.spath1="/home/heo/openCV/change/lastbuild/upload/"
        self.end1= "./end/."
        self.cpath2="/home/heo/openCV/change/lastbuild/detect/"
        self.spath2="/home/heo/openCV/change/lastbuild/upload2/"
        self.end2= "./end2/."
    


    def clisock(self):
        self.sockmsg = ''
        addr = (self.servip, self.servport)
        size = 1024
        print(str(addr) + " sock conneting...")

        self.c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c_sock.connect(addr)
        self.recvmsg()
        self.sendmsg("클라이언트와 정상적으로 연결됨!")
            


    def __del__(self):
        self.cam.release()
        self.sendmsg("exit")
        self.c_sock.close()

    def sendmsg(self, msg):
        self.c_sock.send(msg.encode())

    def recvmsg(self):
        while True:
            msg = self.c_sock.recv(1024)
            if msg is not None:
                break
        msg = msg.decode('utf-8')
        print("serv: " + msg)
        self.sockmsg = msg

    def detectmod(self):
        recordcheck = False
        timecheck = 0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')    
        self.camreset()

        while(True):
            img = self.getcframe()
            if recordcheck == True:
                out.write(img)
                end = time.time()
                timecheck = end - start
                print(str(timecheck))
                if timecheck > 1.5 : #영상 길이
                    out.release()
                    recordcheck = False
                    self.ftpupload(2) # 영상 업로드함
                    #이부분에 소켓 


                    self.sendmsg("upload2")
                    self.recvmsg()
                    time.sleep(2)
                    print("판정결과 : " + self.sockmsg)
                    self.TTS("판정결과 " + self.sockmsg)

#                    self.cam = cv2.VideoCapture(0)
                    time.sleep(1)
                    self.camreset()

                    timecheck = 0



            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                if x > 10 and y > 10 :
                    cv2.rectangle(img, (x-10,y-10), (x+w+10,y+h+10), (255,0,0), 2)
                else:
                    cv2.rectangle(img, (x,y), (x+w+10,y+h+10), (255,0,0), 2)     

                if recordcheck == False:
                    outputFile =  "detect/" + datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S') +".mp4"
                    out = cv2.VideoWriter(outputFile, fourcc, 10.0,(640,480))
                    recordcheck = True
                    start = time.time()
                    out.write(img)

            cv2.imshow('image', img)    #화면 보여줌


            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break



    def user_input(self):
        count = 0
        face_id = input('\n id를 입력해 주세요 : ')  #얼굴인식할 사람의 id를 입력받음
        face_name = input('\n name을 입력해 주세요 : ')  #얼굴인식할 사람의 name을 입력받음
        while(True):
            img = self.getcframe()   #카메라 읽기
            #img = cv2.flip(img, -1) # 상하반전 -1 or 1
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                count += 1  #반복문 카운트
                filename = str(face_id)+ "_" + str(face_name) + "_" + str(count) + ".jpg"
                cv2.imwrite("dataset/id_" +filename , img[y:y+h+2, x:x+w+2])  
                #dataset/ID.사용자id_이름_표본번호.jpg
                if x > 10 and y > 10 :
                    cv2.rectangle(img, (x-10,y-10), (x+w+10,y+h+10), (255,0,0), 2)
                else:
                    cv2.rectangle(img, (x,y), (x+w+10,y+h+10), (255,0,0), 2)     
            cv2.imshow('image', img)    #화면 보여줌
            k = cv2.waitKey(100) & 0xff #  'ESC' 누르면 취소
            if k == 27:
                break
            elif count >= 20: # 얼굴인식 러닝을 위해 사진을 찍을 표본수 #20장
                count = 0
                break

        f = open("filed",'a') #id랑 이름만 따로 텍스트 저장
        data = "%s %s\n" %(face_id, face_name)
        f.write(data)
        self.ftpupload(1)
        self.sendmsg("1")
        self.camreset()

    def camreset(self): # 전송하기전 프레임이 남아있는 경우가 있어서 방지목적
        start = time.time()
        while True: 
            img = self.getcframe()   #카메라 읽기
            cv2.imshow('image', img)    #화면 보여줌
            time.sleep(0.1)
            end = time.time()
            if (end - start) > 1:
                break

    def ftpupload(self, kind):
        #ftp 업로드
        print("\n\n FTP upload ")
        ftp = ftplib.FTP()

        #kind 1: 사용자 등록 ftp, 2: 감지영상 ftp

        if kind == 1:
            cpath = self.cpath1
            spath = self.spath1
            end = self.end1
        
        else:
            cpath = self.cpath2
            spath = self.spath2
            end = self.end2

        with ftplib.FTP() as ftp:
            ftp.connect(self.ftpip,self.ftpport)
            ftp.login(self.ftpid, self.ftppass)
            try:
                ftp.mkd(spath)
            except Exception as e:
                print(" ")

            ftp.cwd(spath)
            list = os.listdir(cpath)
    
            for file in list :
                with open(file=cpath+ '/{}'.format(file), mode= 'rb') as f:
                    ftp.storbinary('STOR {}'.format(file), f)
                    os.system('mv '+cpath+ file +" "+ end)

            print("upload complete\n")

    def getcframe(self):
        ret, frame = self.cam.read()

        return frame

    def TTS(self, text):
        temp = "temp1"
        tts = gTTS(text, lang='ko', slow=False)
        tts.save(temp)
        trans = AudioSegment.from_mp3(temp)
        trans.export(temp, format="wav")
        os.system("aplay " + temp)


if __name__ == '__main__':
    print("초기 설정 실행중")
    face_rasp = Facerasp()

    print("소켓 연결 진행중")
    face_rasp.clisock()  # 클라이언트 소켓 테스트용

    #사용자 등록이나 종료시 감지모드 off 상태에서
    print("초기 설정 실행 완료 , q 입력시 감지모드 on / off , 1 입력시 사용자 등록")
    face_rasp.detectmod() #기본 감지모드 실행 (default)

   # face_rasp.ftpupload(1) #ftp 모듈 테스트용 이것만 실행시 나갈때 ctrl + c 로
   # face_rasp.ftpupload(2)

    while True:

        check = cv2.waitKey(10) & 0xFF
        #감지모드 종료된 상태에서 (q토글) ESC 누르면 종료
        if check == 27:
            break
        #q를 누르면 감지모드 ON/OFF
        if check == ord("q"):
            face_rasp.detectmod()
        #1을 누르면 사용자 등록모드
        if check == ord("1"):
            face_rasp.user_input()


    print("\n 프로세스가 종료됩니다")
    cv2.destroyAllWindows()





