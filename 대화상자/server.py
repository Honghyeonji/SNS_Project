from threading import Thread
from socket import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject
 
class ServerSocket(QObject):
 
    drawing_signal = pyqtSignal(list)
    update_signal = pyqtSignal(tuple, bool)
    recv_signal = pyqtSignal(str)
 
    def __init__(self, parent):        
        super().__init__()
        self.parent = parent
        self.bListen = False       
        self.clients = []
        self.ip = []
        self.threads = []
 
        self.update_signal.connect(self.parent.updateClient)  
        self.recv_signal.connect(self.parent.updateMsg)
    def handle_client(self, client_socket, addr):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break

                # 받은 데이터가 좌표 데이터인지 확인
                if data.startswith(b'Drawing Coordinates:'):
                    coordinates = eval(data.split(b':', 1)[1].decode())
                    self.drawing_signal.emit(coordinates)

                    # 새로운 좌표가 도착할 때마다 모든 클라이언트에게 전송
                    for client_addr, client_socket in self.clients.items():
                        if client_addr != addr:
                            client_socket.sendall(data)

                elif data.startswith(b'Client:'):
                    msg = data.decode('utf-8')
                    self.recv_signal.emit(msg)

        except Exception as e:
            print(f"Error receiving data from {addr}: {e}")
        finally:
            client_socket.close()
            self.removeClient(addr, client_socket)
         
    def __del__(self):
        self.stop()
 
    def start(self, ip, port):
        self.server = socket(AF_INET, SOCK_STREAM)            
 
        try:
            self.server.bind( (ip, port))
        except Exception as e:
            print('Bind Error : ', e)
            return False
        else:                 
            self.bListen = True
            self.t = Thread(target=self.listen, args=(self.server,))
            self.t.start()
            print('Server Listening...')
 
        return True
 
    def stop(self):
        self.bListen = False
        if hasattr(self, 'server'):            
            self.server.close()            
            print('Server Stop')
 
    def listen(self, server):
        while self.bListen:
            server.listen(5)   
            try:
                client, addr = server.accept()
            except Exception as e:
                print('Accept() Error : ', e)
                break
            else:                
                self.clients.append(client)
                self.ip.append(addr)                
                self.update_signal.emit(addr, True)                
                t = Thread(target=self.receive, args=(addr, client))
                self.threads.append(t)
                t.start()                
                 
        self.removeAllClients()
        self.server.close()
 
    def receive(self, addr, client_socket):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                print(data)
                # 받은 데이터가 좌표 데이터인지 확인
                if data.startswith(b'Drawing Coordinates:'):
                    self.parent.handle_drawing_coordinates(data) 

    
                else:
                    msg = data.decode('utf-8')
                    self.recv_signal.emit(msg)

        except Exception as e:
            print(f"Error receiving data from {addr}: {e}")
        finally:
            client_socket.close()
            self.removeClient(addr, client_socket)
    def send(self, msg):
        try:
            for c in self.clients:
                c.send(msg.encode())
        except Exception as e:
            print('Send() Error : ', e)
 
    def removeClient(self, addr, client):
        # find closed client index
        idx = -1
        for k, v in enumerate(self.clients):
            if v == client:
                idx = k
                break
 
        client.close()
        self.ip.remove(addr)
        self.clients.remove(client)
 
        del(self.threads[idx])
        self.update_signal.emit(addr, False)
        self.resourceInfo()
 
    def removeAllClients(self):
        for c in self.clients:
            c.close()
 
        for addr in self.ip:
            self.update_signal.emit(addr, False)
 
        self.ip.clear()
        self.clients.clear()
        self.threads.clear()
 
        self.resourceInfo()
 
    def resourceInfo(self):
        print('Number of Client ip\t: ', len(self.ip) )
        print('Number of Client socket\t: ', len(self.clients) )
        print('Number of Client thread\t: ', len(self.threads) )