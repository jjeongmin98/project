#serv.py
import socket
print("1. 소켓생성")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("2. 바인딩")
sock.bind(("192.168.55.20", 6666))
print("3. 접속대기")
sock.listen()
print("4. 접속수락")
c_sock, addr = sock.accept()
print("5. 데이터수신")
recevie_data = c_sock.recv(1024)
print("수신된 데이터:{}".format(recevie_data))
print("6. 접속종료")
c_sock.close()
sock.close()

#client.py
import socket
print("1.소켓생성")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("3.접속시도")
sock.connect(("192.168.55.20", 6666))
print("5.데이터 송신")
sock.sendall(bytes("Hello socket", "utf-8"))
print("6.접속 종료")
sock.close()
