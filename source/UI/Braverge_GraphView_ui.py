
##
# creating versioning graph view
##

from PyQt5.QtWidgets import (
     QGraphicsScene, QGraphicsView
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF

class GraphView(QGraphicsView):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.node_map = {}  # id(QStandardItem) -> (ellipse, rx, ry)
        self.scale_factor = 1.0

        # Visual improvements
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setAlignment(Qt.AlignCenter)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Draw model initially
        self.draw_model(model)

    # -------------------------------
    # DRAW MODEL
    # -------------------------------
    def draw_model(self, model):
        self.scene.clear()
        self.node_map.clear()

        root = model.invisibleRootItem()
        start_y = 0
        vertical_spacing = 180  # increase vertical space for clean layout

        # Compute subtree width recursively
        def compute_width(item):
            if item.rowCount() == 0:
                return 1
            return sum(compute_width(item.child(i, 0)) for i in range(item.rowCount()))

        # Draw nodes recursively
        def draw_node(item, x, y, prev_center=None, prev_rx=None, prev_ry=None):
            if item is None:
                return

            ellipse_w, ellipse_h = 120, 60
            rx, ry = ellipse_w / 2, ellipse_h / 2

            # Draw ellipse
            ellipse = self.scene.addEllipse(x, y, ellipse_w, ellipse_h, QPen(Qt.black, 2), QBrush(Qt.white))

            # Draw text centered
            text = self.scene.addText(item.text())
            text_rect = text.boundingRect()
            text.setPos(x + (ellipse_w - text_rect.width()) / 2, y + (ellipse_h - text_rect.height()) / 2)
            text.setParentItem(ellipse)

            self.node_map[id(item)] = (ellipse, rx, ry)

            # Draw edge from previous node
            if prev_center is not None:
                child_center = QPointF(x + rx, y + ry)
                self.draw_edge(prev_center, child_center, prev_rx, prev_ry, rx, ry)

            child_count = item.rowCount()
            if child_count == 0:
                return

            # Compute subtree widths
            subtree_widths = [compute_width(item.child(i, 0)) for i in range(child_count)]
            total_width = sum(subtree_widths)

            base_spacing = 140  # base horizontal spacing between subtrees (increased)
            extra_gap = 40      # 🔹 extra horizontal space for arrows
            spacing_factor = base_spacing + extra_gap  # total spacing per subtree

            cur_x = x - total_width * spacing_factor / 2
            prev_child_center = None
            prev_child_rx = prev_child_ry = None

            for i in range(child_count):
                child = item.child(i, 0)
                child_width = subtree_widths[i]
                child_x = cur_x + child_width * spacing_factor / 2
                child_y = y + vertical_spacing

                # connect from parent (first child) or previous child
                connect_from_center = QPointF(x + rx, y + ry) if i == 0 else prev_child_center
                connect_from_rx = rx if i == 0 else prev_child_rx
                connect_from_ry = ry if i == 0 else prev_child_ry

                draw_node(child, child_x, child_y, connect_from_center, connect_from_rx, connect_from_ry)

                prev_child_center = QPointF(child_x + rx, child_y + ry)
                prev_child_rx, prev_child_ry = rx, ry
                cur_x += child_width * spacing_factor

        # Draw all top-level nodes
        x_offset = 0
        for i in range(root.rowCount()):
            draw_node(root.child(i, 0), x_offset, start_y)
            x_offset += compute_width(root.child(i, 0)) * 120  # spacing between top-level nodes

        # Auto-scale view
        self.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.scale(1.4, 1.4)   # 🔹 Make the graph appear ~40% larger

    # -------------------------------
    # RESIZE EVENT
    # -------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        #self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    # -------------------------------
    # EDGE DRAWING
    # -------------------------------
    def draw_edge(self, parent_center, child_center, parent_rx, parent_ry, child_rx, child_ry, pen=QPen(Qt.black, 2)):
        dx = child_center.x() - parent_center.x()
        dy = child_center.y() - parent_center.y()
        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            return

        ux, uy = dx / length, dy / length
        scale_px = parent_rx / abs(ux) if ux != 0 else float('inf')
        scale_py = parent_ry / abs(uy) if uy != 0 else float('inf')
        parent_edge = QPointF(parent_center.x() + ux * min(scale_px, scale_py),
                              parent_center.y() + uy * min(scale_px, scale_py))

        scale_cx = child_rx / abs(ux) if ux != 0 else float('inf')
        scale_cy = child_ry / abs(uy) if uy != 0 else float('inf')
        child_edge = QPointF(child_center.x() - ux * min(scale_cx, scale_cy),
                             child_center.y() - uy * min(scale_cx, scale_cy))

        self.scene.addLine(parent_edge.x(), parent_edge.y(), child_edge.x(), child_edge.y(), pen)

        # Draw arrowhead
        arrow_size = 10
        perp_x, perp_y = -uy, ux
        p1 = child_edge
        p2 = QPointF(child_edge.x() - arrow_size * ux + 5 * perp_x,
                     child_edge.y() - arrow_size * uy + 5 * perp_y)
        p3 = QPointF(child_edge.x() - arrow_size * ux - 5 * perp_x,
                     child_edge.y() - arrow_size * uy - 5 * perp_y)
        arrow_head = QPolygonF([p1, p2, p3])
        self.scene.addPolygon(arrow_head, pen, QBrush(Qt.black))

    # -------------------------------
    # HIGHLIGHT NODE
    # -------------------------------
    def highlight_node(self, item):
        for ellipse, _, _ in self.node_map.values():
            ellipse.setBrush(QBrush(Qt.white))
        key = id(item)
        if key in self.node_map:
            self.node_map[key][0].setBrush(QBrush(Qt.lightGray))

    # -------------------------------
    # MOUSE ZOOM + PAN
    # -------------------------------
    def wheelEvent(self, event):
        zoom_in = 2.25
        zoom_out = 0.8
        factor = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.scale(factor, factor)
        self.scale_factor *= factor
