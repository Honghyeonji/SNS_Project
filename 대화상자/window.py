from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import socket
import server
 
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
 
class CWidget(QWidget):
    def __init__(self):
        super().__init__()
 
        self.s = server.ServerSocket(self)
        
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle('서버')
         
        ipbox = QHBoxLayout()
 
        gb = QGroupBox('서버 설정')
        ipbox.addWidget(gb)
 
        box = QHBoxLayout()
 
        label = QLabel('Server IP : 127.0.0.1')
        box.addWidget(label)
 
        label = QLabel('Server Port : 1234')
        box.addWidget(label)   
 
        gb.setLayout(box)
        
        infobox = QHBoxLayout()
        gb = QGroupBox('접속자 정보')
        infobox.addWidget(gb)
 
        box = QHBoxLayout()        
 
        self.guest = QTableWidget()        
        self.guest.setColumnCount(2)      
        self.guest.setHorizontalHeaderItem(0, QTableWidgetItem('ip'))
        self.guest.setHorizontalHeaderItem(1, QTableWidgetItem('port'))                
 
        box.addWidget(self.guest)
        gb.setLayout(box)
      
        gb = QGroupBox('채팅')        
        infobox.addWidget(gb)
 
        box = QVBoxLayout()        
 
        self.msg = QListWidget()
        box.addWidget(self.msg)
 
        hbox = QHBoxLayout()

        self.sendmsg = QLineEdit()
        self.sendmsg.setFixedHeight(50)
        hbox.addWidget(self.sendmsg)
         
        self.sendbtn = QPushButton('보내기')
        self.sendbtn.clicked.connect(self.sendMsg)
        self.sendbtn.setFixedHeight(50)
        hbox.addWidget(self.sendbtn)
 
        self.clearbtn = QPushButton('채팅창 지움')
        self.clearbtn.clicked.connect(self.clearMsg)
        self.clearbtn.setFixedHeight(50)
        hbox.addWidget(self.clearbtn)
 
        box.addLayout(hbox)
 
        gb.setLayout(box)
        
        gb = QGroupBox('그림판')
        infobox.addWidget(gb)

        box = QVBoxLayout()
        self.drawingbtn = QPushButton('그림판')
        self.drawingstate = False
        self.drawingbtn.clicked.connect(self.drawing)
        box.addWidget(self.drawingbtn)

        gb.setLayout(box)
 
        vbox = QVBoxLayout()
        vbox.addLayout(ipbox)       
        vbox.addLayout(infobox)
        self.setLayout(vbox)
         
        self.show()

        self.s.start("127.0.0.1", 1234)
    
    def drawing(self):
        ## 여기다 그림판 로직 추가
        if self.drawingstate:
            self.drawingbtn.setText('그림판 종료')
            self.drawingstate = False
        else:
            self.drawingbtn.setText('그림판')
            self.drawingstate = True
 
    def updateClient(self, addr, isConnect = False):        
        row = self.guest.rowCount()        
        if isConnect:        
            self.guest.setRowCount(row+1)
            self.guest.setItem(row, 0, QTableWidgetItem(addr[0]))
            self.guest.setItem(row, 1, QTableWidgetItem(str(addr[1])))
        else:            
            for r in range(row):
                ip = self.guest.item(r, 0).text() # ip
                port = self.guest.item(r, 1).text() # port
                if addr[0]==ip and str(addr[1])==port:
                    self.guest.removeRow(r)
                    break
 
    def updateMsg(self, msg):
        self.msg.addItem(QListWidgetItem(msg))
        self.msg.setCurrentRow(self.msg.count()-1)
 
    def sendMsg(self):
        if not self.s.bListen:
            self.sendmsg.clear()
            return
        sendmsg = "Server[" + str(self.s.server.getsockname()[1]) + "]" + self.sendmsg.text()
        self.updateMsg(sendmsg)
        print(sendmsg)
        self.s.send(sendmsg)
        self.sendmsg.clear()
 
    def clearMsg(self):
        self.msg.clear()
 
    def closeEvent(self, e):
        self.s.stop()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())