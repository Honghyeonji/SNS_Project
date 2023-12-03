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
        while self.bConnect:            
            try:
                recv = self.client.recv(1024)                
            except Exception as e:
                print('Recv() Error :', e)                
                break
            else:
                msg = str(recv, encoding='utf-8')
                if msg.startswith('Drawing Coordinates:'):
                    coordinates_str = msg.split('[', 1)[1].rsplit(']', 1)[0]
                    coordinates_list = eval('[' + coordinates_str + ']')
                    print('[RECV]:', msg)
                    self.parent.handle_drawing_receive_coordinates(coordinates_list)  # 좌표 리스트만 전달
                elif msg:
                    self.recv_signal.emit(msg)
                    print('[RECV]:', msg)

                # if msg:
                #     self.recv_signal.emit(msg)
                #     print('[RECV]:', msg)

        self.stop()
 
    def send(self, msg):
        if not self.bConnect:
            return
 
        try:
            self.client.send(msg.encode())
        except Exception as e:
            print('Send() Error : ', e)
