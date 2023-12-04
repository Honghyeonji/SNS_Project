from threading import Thread
from socket import *
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import random

class ServerSocket(QObject):
 
    update_signal = pyqtSignal(tuple, bool)
    msg_signal = pyqtSignal(str)
    quiz_signal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.bListen = False
        self.clients = []
        self.ip = []
        self.threads = []

        self.quizing = False
        self.quizClient = None
        self.quizWord = None

        self.update_signal.connect(self.parent.updateClient)
        self.msg_signal.connect(self.parent.updateMsg)
        self.quiz_signal.connect(self.parent.guessWord)
         
    def __del__(self):
        self.stop()

    def start(self, ip, port):
        self.server = socket(AF_INET, SOCK_STREAM)

        try:
            self.server.bind((ip, port))
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
                print(data)
                print("receiving")
                if data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xFF\xD8\xFF\xE0') or data.startswith(b'\xFF\xD8\xFF\xE1'):
                    self.parent.handle_drawing_coordinates(data) 
                    self.sendIMG(data, client)
                else:
                    msg = data.decode('utf-8')
                    if self.quizing:
                        if self.quizWord in msg:
                            self.quiz_signal.emit(msg)
                            self.quizCorrect(client)
                        else:
                            self.msg_signal.emit(msg)
                            self.sendmsg(msg, client)
                    else:
                        self.msg_signal.emit(msg)
                        self.sendmsg(msg, client)
        except Exception as e:
            print(f"Error receiving data from {addr}: {e}")
        finally:
            client.close()
            self.removeClient(addr, client)
        
 
    def sendmsg(self, msg, client=None):
        try:
            if client:
                for c in self.clients:
                    if c != client:
                        c.send(msg.encode())
            else:
                for c in self.clients:
                    c.send(msg.encode())
        except Exception as e:
            print('Send() Error : ', e)

    def sendIMG(self, msg, client=None):
        try:
            if client:
                for c in self.clients:
                    if c != client:
                        c.sendall(msg)
            else:
                for c in self.clients:
                    c.sendall(msg)
        except Exception as e:
            print('imgSend() Error : ', e)
        
    def sendQuiz(self, word):
        try:
            self.quizClient = self.clients[random.randint(0, len(self.clients)-1)]
            self.quizWord = word
            for c in self.clients:
                if c == self.quizClient:
                    msg = f"게임을 시작합니다.\n"
                    c.send(msg.encode())
                    msg = f"주어진 단어를 보고 그림을 그려 전송해주세요.\n"
                    c.send(msg.encode())
                    msg = f"우측 그림판을 통해 그릴 수 있습니다.\n"
                    c.send(msg.encode())
                    msg = f"랜덤 단어: {word}\n"
                    c.send(msg.encode())
                else:
                    msg = f"게임을 시작합니다.\n"
                    c.send(msg.encode())
                    msg = f"단어가 Client[{str(self.quizClient.getsockname()[1])}]유저에게 전송 되었습니다. Client[{str(self.quizClient.getsockname()[1])}]유저가 전송한 그림을 보고 맞춰주세요.\n"
                    c.send(msg.encode())
                    msg = f"그림이 도착한 후 그림판 버튼을 누르면 그림을 볼 수 있습니다.\n"
                    c.send(msg.encode())

            self.quizing = True
        except Exception as e:
            print('sendQuizSend() Error : ', e)
            
    def quizCorrect(self, client=None):
        try:
            for c in self.clients:
                if c == client:
                    msg = f"축하합니다. 정답을 맞췄습니다! : 맞춘 단어:{self.quizWord}.\n"
                    c.send(msg.encode())
                    msg = f"게임을 종료합니다.\n"
                    c.send(msg.encode())
                else:
                    msg = f"Client[{str(client.getsockname()[1])}]님이 정답을 맞췄습니다! : 맞춘 단어:{self.quizWord}.\n"
                    c.send(msg.encode())
                    msg = f"게임을 종료합니다.\n"
                    c.send(msg.encode())
            self.quizing=False
            self.quizWord=None
            self.quizClient=None
        except Exception as e:
            print('quizCorrectSend() Error : ', e)

    def removeClient(self, addr, client):
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
