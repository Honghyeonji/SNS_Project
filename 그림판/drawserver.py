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
        self.drawing_coordinates = []  # List to store drawing coordinates

    def paintEvent(self, e):
        canvas = QPainter(self)
        canvas.drawImage(self.rect(), self.image, self.image.rect())

    def update_drawing(self, coordinates):
        painter = QPainter(self.image)
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        for start_point, end_point in zip(coordinates, coordinates[1:]):
            painter.drawLine(start_point[0], start_point[1], end_point[0], end_point[1])

        self.update()

class DrawingThread(QThread):
    drawing_signal = pyqtSignal(tuple)

    def __init__(self, server_app):
        super().__init__()
        self.server_app = server_app

    def run(self):
        self.server_app.show()
        self.exec_()

class ServerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        self.drawing_canvas = DrawingCanvas()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Server - Real-time Drawing')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.addWidget(self.drawing_canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_drawing_thread(self):
        self.drawing_thread = DrawingThread(self)
        self.drawing_thread.drawing_signal.connect(self.handle_drawing_signal)
        self.drawing_canvas.drawing_signal.connect(self.drawing_thread.drawing_signal.emit)
        self.drawing_thread.start()

    def handle_drawing_signal(self, coordinates):
        print("Received coordinates:", coordinates)
        self.drawing_canvas.update_drawing(coordinates)

class Server(QObject):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")

        self.client_socket, self.client_address = self.server_socket.accept()

        self.server_app = ServerApp()  # 서버 GUI 초기화
        self.server_app.show()  # 서버 GUI 표시
        self.server_app.start_drawing_thread()

    def start(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                coordinates = pickle.loads(data)
                coordinates_tuple = tuple(map(tuple, coordinates))  # 리스트를 튜플로 변환
                print("Received coordinates:", coordinates_tuple)
                self.server_app.drawing_canvas.drawing_signal.emit(coordinates_tuple)
        finally:
            self.server_socket.close()


app = QApplication(sys.argv)
server = Server('127.0.0.1', 12345)
server.start()
sys.exit(app.exec_())
