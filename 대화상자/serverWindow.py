from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import random
from server import *

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class DrawingCanvas(QWidget):
    drawing_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage(QSize(400, 400), QImage.Format_RGB32)
        self.image.fill(Qt.white)

    def paintEvent(self, e):
        canvas = QPainter(self)
        canvas.drawImage(self.rect(), self.image, self.image.rect())

    def update_drawing(self, image_data):
        image = QImage.fromData(image_data)
        self.image = image
        self.update()

class DrawingDialog(QDialog):
    def __init__(self, image_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle('그림판')
        self.resize(800, 600)
        self.drawing_canvas = DrawingCanvas(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.drawing_canvas)

        
        self.drawing_canvas.update_drawing(image_data)  # 좌표를 화면에 업데이트

    def closeEvent(self, event):
        self.parent().set_drawingstate(False)  # 또는 True로 변경하면 됩니다.
        super().closeEvent(event)
        

class CWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QImage(QSize(400, 400), QImage.Format_RGB32) 
        self.drawing_canvas = DrawingCanvas(self)
        self.random_word = None

        self.s = ServerSocket(self)  # Pass self as the parent
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
        self.drawingbtn = QPushButton('그림판 보기')
        self.drawingstate = False
        self.drawingbtn.clicked.connect(self.drawing)
        box.addWidget(self.drawingbtn)

        self.wordbtn = QPushButton('단어 출제')
        box.addWidget(self.wordbtn)
        self.wordbtn.clicked.connect(self.displayRandomWord)
        gb.setLayout(box)

        gb.setLayout(box)

        vbox = QVBoxLayout()
        vbox.addLayout(ipbox)
        vbox.addLayout(infobox)
        self.setLayout(vbox)

        self.show()

        gb.setLayout(box)

        vbox = QVBoxLayout()
        vbox.addLayout(ipbox)
        vbox.addLayout(infobox)
        self.setLayout(vbox)

        self.show()

        self.s.start("127.0.0.1", 1234)

    def show_drawing_dialog(self):
        dialog = DrawingDialog(self.image_data,self)
        dialog.exec_()

    def set_drawingstate(self, state):
        self.drawingstate = state
        print(f"drawingstate가 {state}로 변경되었습니다.")
        self.drawingbtn.setText('그림판 시작')
        self.drawingstate = False

    def drawing(self):
        if self.drawingstate:
            self.drawingbtn.setText('그림판 시작')
            self.drawingstate = False

        else:
            self.drawingbtn.setText('그림판 종료')
            self.drawingstate = True

            self.show_drawing_dialog()

    def handle_drawing_coordinates(self, image_data):
       self.image_data = image_data

    def updateClient(self, addr, isConnect=False):
        row = self.guest.rowCount()
        if isConnect:
            self.guest.setRowCount(row + 1)
            self.guest.setItem(row, 0, QTableWidgetItem(addr[0]))
            self.guest.setItem(row, 1, QTableWidgetItem(str(addr[1])))
        else:
            for r in range(row):
                ip = self.guest.item(r, 0).text()  # ip
                port = self.guest.item(r, 1).text()  # port
                if addr[0] == ip and str(addr[1]) == port:
                    self.guest.removeRow(r)
                    break

    def updateMsg(self, msg):
        self.msg.addItem(QListWidgetItem(msg))
        self.msg.setCurrentRow(self.msg.count() - 1)

    def sendMsg(self):
        if not self.s.bListen:
            self.sendmsg.clear()
            return
        sendmsg = "Server[" + str(self.s.server.getsockname()[1]) + "]" + self.sendmsg.text()
        self.updateMsg(sendmsg)
        print(sendmsg)
        self.s.sendmsg(sendmsg)
        if self.sendmsg.text() and self.random_word:
            if self.random_word in self.sendmsg.text():
                self.updateMsg(f"서버가 정답을 맞췄습니다!")
                self.updateMsg(f"맞춘 단어: {self.random_word}")
                self.updateMsg(f"게임을 종료합니다.")
                sendmsg = f"Server[{str(self.s.server.getsockname()[1])}]님이 정답을 맞췄습니다! : 맞춘단어:{self.random_word}\n"
                self.s.sendmsg(sendmsg)
                self.random_word = None
                self.s.quizing=False
                self.s.quizWord=None
                self.s.quizClient=None
        self.sendmsg.clear()

    def clearMsg(self):
        self.msg.clear()

    def closeEvent(self, e):
        self.s.stop()

    def displayRandomWord(self):
        if (self.random_word == None):
            words = ["사과", "바나나", "오렌지", "포도", "체리", "딸기", "망고", "꽃", "달", "나무", "집" ]
            self.random_word = random.choice(words)

            self.updateMsg("게임을 시작합니다.")
            self.updateMsg("단어가 전송 되었습니다. 상대방이 전송한 그림을 보고 맞춰주세요.")
            self.updateMsg("그림이 도착한 후 그림판 버튼을 누르면 그림을 볼 수 있습니다.")

            self.s.sendQuiz(self.random_word)

        else:
            self.updateMsg("이미 진행 중 입니다.")

    def guessWord(self, msg):
        self.updateMsg(msg)
        self.updateMsg(f"정답을 맞췄습니다!")
        self.updateMsg(f"맞춘 단어: {self.random_word}")
        self.updateMsg(f"게임을 종료합니다.")
        self.random_word = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())
