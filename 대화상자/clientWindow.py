from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import client
import sys
import socket
import threading

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class DrawingCanvas(QWidget):
    drawing_signal = pyqtSignal(str, bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage(QSize(400, 400), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.drawing = False
        self.brush_size = 5
        self.brush_color = Qt.black
        self.last_point = QPoint()


    def paintEvent(self, e):
        canvas = QPainter(self)
        canvas.drawImage(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = e.pos()

    def mouseMoveEvent(self, e):
        if (e.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(self.last_point, e.pos())
            self.last_point = e.pos()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drawing = False
    def get_drawing_coordinates(self):
        return self.drawing_coordinates
    def get_image_data(self):
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        self.image.save(buffer, "PNG")
        return byte_array.data()


    

class DrawingDialog(QDialog):
    drawing_signal = pyqtSignal(str,bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('그림판')
        self.resize(800, 600)
        self.drawing_canvas = DrawingCanvas(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.drawing_canvas)

        # 버튼을 넣을 QHBoxLayout
        button_layout = QHBoxLayout()
        send_button = QPushButton("전송", self)
        send_button.clicked.connect(self.send_image_button)
        button_layout.addWidget(send_button)

        # 전체를 감싸는 QVBoxLayout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def send_image_button(self):
        image_data = self.drawing_canvas.get_image_data()
        image_data_list = list(image_data)
        self.drawing_signal.emit("drawing_image", image_data)
        
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
        self.drawingbtn.clicked.connect(self.drawing)

        self.show()
    def show_drawing_dialog(self):
        dialog = DrawingDialog(self)
        dialog.drawing_signal.connect(self.handle_drawing_image)  # Connect the signal
        dialog.exec_()

    def handle_drawing_image(self, identifier, image_data):

        if identifier == "drawing_image":
            image_data_bytes = bytes(image_data)

            self.c.send(image_data_bytes)




    def drawing(self):
        if self.drawingstate:
            self.drawingbtn.setText('그림판 종료')
            self.drawingstate = False
            self.show_drawing_dialog()
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
        if self.c.bConnect:  # Check if connected before attempting to sen
            sendmsg = "Client[" + str(self.c.client.getsockname()[1]) + "]" + self.sendmsg.toPlainText()
            self.c.send(sendmsg)
            self.updateMsg(sendmsg)
            self.sendmsg.clear()
        else:
            print("Not connected. Cannot send message.")
 
    def clearMsg(self):
        self.recvmsg.clear()
 
    def closeEvent(self, e):
        self.c.stop()       
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())