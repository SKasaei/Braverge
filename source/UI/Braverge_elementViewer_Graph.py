from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class GraphWidget(QGraphicsView):
    def __init__(self, image_path, parent=None, initial_scale=0.5):
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._zoom = 0
        self._pixmap_item = None
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.load_image(image_path, initial_scale)

    def load_image(self, image_path, initial_scale=0.5):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return
        self._scene.clear()
        
        # Smooth scaling
        pixmap = pixmap.scaled(pixmap.width(), pixmap.height(),
                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self._pixmap_item)

        self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
        self.scale(initial_scale, initial_scale)


    def wheelEvent(self, event):
        """Zoom in/out with mouse wheel"""
        if not self._pixmap_item:
            return
        angle = event.angleDelta().y()
        factor = 1.25 if angle > 0 else 0.8
        self._zoom += 1 if angle > 0 else -1
        if -10 < self._zoom < 10:
            self.scale(factor, factor)

