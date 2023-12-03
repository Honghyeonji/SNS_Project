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

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                # 받은 데이터가 좌표 데이터인지 확인
                if data.startswith(b'Drawing Coordinates:'):
                    coordinates = eval(data.split(b':', 1)[1].decode())
                    self.client_coordinates[addr] = coordinates

                    # 새로운 좌표가 도착할 때마다 모든 클라이언트에게 전송
                    for client, client_socket in self.clients.items():
                        if client != addr:
                            client_socket.sendall(data)
            except:
                break
         
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
 
    def receive(self, addr, client):

        try:
            while True:
                data = client.recv(4096)
                if not data:
                    break
                # identifier, image_data = pickle.loads(data)
                # print(data)
                self.parent.handle_drawing_coordinates(data)  # 좌표 리스트만 전달
                # Process the binary data as needed
                # For example, you can save it to a file or perform other image processing
                with open('received_image.png', 'ab') as file:
                    file.write(data)

        except Exception as e:
            print(f"Error receiving data from {addr}: {e}")
        finally:
            client.close()
            
        self.removeClient(addr, client)
 
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