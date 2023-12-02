from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt5.QtCore import Qt
import sys

class GraphicsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('좌표 그래프')
        self.setGeometry(100, 100, 800, 600)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # 좌표 리스트 (예시)
        coordinates = [(299, 226), (297, 223), (293, 219), (290, 216), (286, 212), (272, 202), (267, 199), (254, 194), (244, 194), (236, 194), (196, 212), (185, 220), (144, 278), (137, 299), (134, 315), (139, 358), (142, 365), (155, 370), (165, 369), (172, 368), (227, 338), (237, 328), (278, 278), (283, 268), (286, 257), (287, 239), (281, 229), (251, 210), (239, 206), (218, 203), (170, 205), (162, 209), (159, 212), (159, 212), (160, 212), (164, 212), (171, 210), (194, 198), (203, 193), (215, 185), (224, 174), (226, 169), (226, 165), (224, 160), (222, 158), (217, 156), (217, 155), (216, 155)]

        # 그래프 그리기
        self.draw_coordinates(coordinates)

    def draw_coordinates(self, coordinates):
        pen = Qt.black
        for i in range(len(coordinates) - 1):
            start_point = coordinates[i]
            end_point = coordinates[i + 1]
            
            # 직선 그리기
            line = QGraphicsLineItem(start_point[0], start_point[1], end_point[0], end_point[1])
            line.setPen(pen)
            self.scene.addItem(line)
            
            # 점 그리기 (원 형태)
            ellipse = QGraphicsEllipseItem(end_point[0] - 5, end_point[1] - 5, 10, 10)
            ellipse.setPen(pen)
            self.scene.addItem(ellipse)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphicsWindow()
    window.show()
    sys.exit(app.exec_())
