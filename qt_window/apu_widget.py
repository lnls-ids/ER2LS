from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter


class APUWidget:

    def __init__(self, graphics_view):

        self.scene = QGraphicsScene()
        graphics_view.setScene(self.scene)

        self.scene.setBackgroundBrush(QColor(187, 187, 221))

        graphics_view.setRenderHint(QPainter.Antialiasing)

        self.upper = []
        self.lower = []

        self.block_w = 4*5
        self.block_h = 20
        self.spacing = 2

        self.phase = 0

        self.draw()

    def draw(self):

        self.scene.clear()

        self.upper.clear()
        self.lower.clear()

        colors = [
            QColor(220, 60, 60),
            QColor(60, 100, 220)
        ]

        N = 8

        # Linha superior
        for i in range(N):

            x = i*(self.block_w+self.spacing)

            color = colors[i % 2]

            rect = self.scene.addRect(
                x,
                10,
                self.block_w,
                self.block_h,
                QPen(Qt.black),
                QBrush(color)
            )

            self.upper.append(rect)

        # Linha inferior
        for i in range(N):

            x = i*(self.block_w+self.spacing)

            color = colors[(i+1) % 2]

            rect = self.scene.addRect(
                x,
                45,
                self.block_w,
                self.block_h,
                QPen(Qt.black),
                QBrush(color)
            )

            self.lower.append(rect)

    def set_phase(self, phase_mm):

        pixels = phase_mm*4

        for i, rect in enumerate(self.lower):

            x = i*(self.block_w+self.spacing) + pixels

            rect.setRect(
                x,
                45,
                self.block_w,
                self.block_h
            )

        self.phase = phase_mm
