from threading import *
from socket import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject
 
class ClientSocket(QObject):
    recv_signal = pyqtSignal(str)
    disconn_signal = pyqtSignal()

    def __init__(self, parent):        
        super().__init__()  
        self.parent = parent                
        
        self.recv_signal.connect(self.parent.updateMsg)
        self.disconn_signal.connect(self.parent.updateDisconnect)
 
        self.bConnect = False
         
    def __del__(self):
        self.stop()
 
    def connectServer(self, ip, port):
        self.client = socket(AF_INET, SOCK_STREAM)           
 
        try:
            self.client.connect((ip, port))
        except Exception as e:
            print('Connect Error : ', e)
            return False
        else:
            self.bConnect = True
            self.t = Thread(target=self.receive)
            self.t.start()
            print('Connected')
 
        return True
 
    def stop(self):
        self.bConnect = False       
        if hasattr(self, 'client'):            
            self.client.close()
            del(self.client)
            print('Client Stop') 
            self.disconn_signal.emit()
 
    def receive(self):
        try:
            while True:
                data = self.client.recv(4096)
                if not data:
                    break
                print(data)
                if data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xFF\xD8\xFF\xE0') or data.startswith(b'\xFF\xD8\xFF\xE1'):
                    self.parent.handle_drawing_receive_coordinates(data) 
    
                else:
                    msg = data.decode('utf-8')
                    self.recv_signal.emit(msg)

        except Exception as e:
            print('Recv() Error :', e)
        finally:
            self.stop()

    def send(self, msg):
        if not self.bConnect:
            return
 
        try:
            self.client.send(msg.encode())
        except Exception as e:
            print('Send() Error : ', e)
    def sendIMG(self, msg):
        if not self.bConnect:
            return
 
        try:
            self.client.sendall(msg)
            print(f'Sent: {msg}')  # 데이터를 콘솔에 출력
        except Exception as e:
            print('Send() Error : ', e)

