from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import client
 
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
 
class CWidget(QWidget):
    def __init__(self):
        super().__init__()  
         
        self.c = client.ClientSocket(self)
        
        self.initUI()
 
    def __del__(self):
        self.c.stop()
 
    def initUI(self):
        self.setWindowTitle('클라이언트')
         
        # 클라이언트 설정 부분
        ipbox = QHBoxLayout()
 
        gb = QGroupBox('서버 설정')
        ipbox.addWidget(gb)
 
        box = QHBoxLayout()
 
        label = QLabel('Server IP')
        self.ip = QLineEdit()
        box.addWidget(label)
        box.addWidget(self.ip)
 
        label = QLabel('Server Port')
        self.port = QLineEdit()
        box.addWidget(label)
        box.addWidget(self.port)
 
        self.btn = QPushButton('접속')       
        self.btn.clicked.connect(self.connectClicked)
        box.addWidget(self.btn)
 
        gb.setLayout(box)       
  
        infobox = QHBoxLayout()      
        gb = QGroupBox('채팅')        
        infobox.addWidget(gb)
 
        box = QVBoxLayout()
 
        self.recvmsg = QListWidget()
        box.addWidget(self.recvmsg)

        hbox = QHBoxLayout()
        box.addLayout(hbox)
 
        self.sendmsg = QTextEdit()
        self.sendmsg.setFixedHeight(50)
        hbox.addWidget(self.sendmsg)
 
        self.sendbtn = QPushButton('보내기')
        self.sendbtn.setAutoDefault(True)
        self.sendbtn.clicked.connect(self.sendMsg)
        self.sendbtn.setFixedHeight(50)
        hbox.addWidget(self.sendbtn)
         
        self.clearbtn = QPushButton('채팅창 지움')
        self.clearbtn.clicked.connect(self.clearMsg)
        self.clearbtn.setFixedHeight(50)
        hbox.addWidget(self.clearbtn)

        gb.setLayout(box)

        gb = QGroupBox('그림판')
        infobox.addWidget(gb)

        box = QVBoxLayout()
        self.drawingbtn = QPushButton('그림판')
        self.drawingstate = False
        self.drawingbtn.clicked.connect(self.drawing)
        box.addWidget(self.drawingbtn)

        # box.addlayout() 해서 그림판 추가
        # 그림판 버튼은 /그림판 으로 명령어로 넘어가기로 했던 것 대신 그림판 버튼 누르면 그림판으로 넘어가게 하고 싶어서 추가함

        gb.setLayout(box)
 
        vbox = QVBoxLayout()
        vbox.addLayout(ipbox)       

        hbox = QHBoxLayout()
        hbox.addLayout(infobox)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
         
        self.show()

    def drawing(self):
        if self.drawingstate:
            self.drawingbtn.setText('그림판 종료')
            self.drawingstate = False
            ## 여기다 그림판 로직 추가
        else:
            self.drawingbtn.setText('그림판')
            self.drawingstate = True
 
    def connectClicked(self):
        if self.c.bConnect == False:
            ip = self.ip.text()
            port = self.port.text()
            if self.c.connectServer(ip, int(port)):
                self.btn.setText('접속 종료')
            else:
                self.c.stop()
                self.sendmsg.clear()
                self.recvmsg.clear()
                self.btn.setText('접속')
        else:
            self.c.stop()
            self.sendmsg.clear()
            self.recvmsg.clear()
            self.btn.setText('접속')
 
    def updateMsg(self, msg):
        self.recvmsg.addItem(QListWidgetItem(msg))
 
    def updateDisconnect(self):
        self.btn.setText('접속')
 
    def sendMsg(self):
        sendmsg = "Client[" + str(self.c.client.getsockname()[1]) + "]" + self.sendmsg.toPlainText()
        self.c.send(sendmsg)
        self.updateMsg(sendmsg)
        self.sendmsg.clear()
 
    def clearMsg(self):
        self.recvmsg.clear()
 
    def closeEvent(self, e):
        self.c.stop()       
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())
