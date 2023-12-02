import sys
import socket
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class DrawingCanvas(QWidget):
    drawing_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage(QSize(400, 400), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.drawing = False
        self.brush_size = 5
        self.brush_color = Qt.black
        self.last_point = QPoint()
        self.drawing_coordinates = []  # List to store drawing coordinates

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
            self.drawing_coordinates.append((self.last_point.x(), self.last_point.y()))  # Store coordinates
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drawing = False

    def get_drawing_coordinates(self):
        return self.drawing_coordinates

class ClientApp(QMainWindow):
    def __init__(self, server_host, server_port):
        super().__init__()
        self.server_host = server_host
        self.server_port = server_port

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        self.pen = QPen(Qt.red)
        self.pen.setWidth(2)

        self.initUI()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

        self.drawing_canvas = DrawingCanvas()

        # 그림판을 넣을 QVBoxLayout
        drawing_layout = QVBoxLayout()
        drawing_layout.addWidget(self.drawing_canvas)

        # 버튼을 넣을 QHBoxLayout
        button_layout = QHBoxLayout()
        send_button = QPushButton("전송", self)
        send_button.clicked.connect(self.send_coordinates_button)
        button_layout.addWidget(send_button)

        # 전체를 감싸는 QVBoxLayout
        main_layout = QVBoxLayout()
        main_layout.addLayout(drawing_layout)
        main_layout.addLayout(button_layout)

        # 중앙 위젯 설정
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.show()

        self.drawing_canvas.drawing_signal.connect(self.send_coordinates)

    def initUI(self):
        self.setWindowTitle('Client - Real-time Drawing')
        self.setGeometry(100, 100, 800, 600)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
        except Exception as e:
            print("서버에 연결 중 오류 발생:", str(e))
            sys.exit()

    def send_coordinates(self):
        coordinates = self.drawing_canvas.get_drawing_coordinates()
        try:
            data = pickle.dumps(coordinates)
            self.client_socket.send(data)
        except BrokenPipeError:
            print("좌표 전송 중 오류 발생: .")
            self.client_socket.close()
            self.connect_to_server()
        except Exception as e:
            print("좌표 전송 중 오류 발생:", str(e))

    def send_coordinates_button(self):
        self.send_coordinates()

app = QApplication(sys.argv)
client_app = ClientApp('127.0.0.1', 1234)
sys.exit(app.exec_())

