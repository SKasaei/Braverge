from PyQt5.QtWidgets import (
    QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget, QGridLayout, QLabel, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt
import tempfile
import os
from graphviz import Digraph
from UI.Braverge_elementViewer_Graph import GraphWidget  # adjust import if necessary


# -----------------------------
# Helper Functions
# -----------------------------
def add_element_to_tree(parent, element_data):
    """Recursively add element data to QTreeWidgetItem."""
    element_label = element_data.get('element_type', 'Unknown')
    element_id = element_data.get('element_id')
    if element_id:
        element_label += f" (ID: {element_id})"

    element_item = QTreeWidgetItem([element_label])
    parent.addChild(element_item)

    for prop in element_data.get('properties', []):
        prop_name = prop.get('feature_name', 'unknown')
        val = prop.get('value')

        if isinstance(val, dict) and 'element_type' in val:
            prop_item = QTreeWidgetItem([prop_name])
            element_item.addChild(prop_item)
            add_element_to_tree(prop_item, val)
        elif isinstance(val, list):
            prop_item = QTreeWidgetItem([prop_name])
            element_item.addChild(prop_item)
            for item in val:
                if isinstance(item, dict) and 'element_type' in item:
                    add_element_to_tree(prop_item, item)
                else:
                    QTreeWidgetItem(prop_item, [str(item)])
        else:
            prop_item = QTreeWidgetItem([f"{prop_name}: {val}"])
            element_item.addChild(prop_item)

    return element_item


def create_graph_header(text, color_start, color_end):
    """Create QLabel with gradient background for graph headers."""
    header = QLabel(text)
    header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    header.setStyleSheet(f"""
        QLabel {{
            font-weight: bold;
            font-size: 13px;
            color: white;
            padding: 4px;
            border-radius: 6px;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {color_start},
                stop:1 {color_end}
            );
        }}
    """)
    return header


def style_tree_header(header: QHeaderView, color_start: str, color_end: str):
    """Apply horizontal gradient background to QTreeWidget header."""
    header.setStyleSheet(f"""
        QHeaderView::section {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {color_start},
                stop:1 {color_end}
            );
            color: white;
            font-weight: bold;
            font-size: 13px;
            padding: 4px;
            border: 1px solid #999999;
        }}
    """)


# -----------------------------
# Main Viewer Class
# -----------------------------
class ModelViewer(QMainWindow):
    def __init__(self, element_data, scale_factor=1.0):
        super().__init__()
        self.scale_factor = scale_factor
        self.setWindowTitle("Braverge Model Viewer")
        self.resize(int(600 * scale_factor), int(600 * scale_factor))
        self.center_on_screen()

        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # -------------------------
        # Tree
        # -------------------------
        tree = QTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderLabels(["Tree Viewer"])
        add_element_to_tree(tree.invisibleRootItem(), element_data)
        style_tree_header(tree.header(), "#a52800", "#FF8A65")
        layout.addWidget(tree, 0, 0)

        # -------------------------
        # Graph
        # -------------------------
        header = create_graph_header("Graph Viewer", "#a52800", "#FF8A65")
        layout.addWidget(header, 1, 0)

        graph = self.build_graphviz_graph(element_data)
        graph_path = self._save_graph_to_png(graph, "element_graph")
        graph_widget = GraphWidget(graph_path, initial_scale=0.4)
        layout.addWidget(graph_widget, 2, 0)
        graph_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # -------------------------
        # Layout Stretch Rules
        # -------------------------
        layout.setRowStretch(0, 1)  # Tree
        layout.setRowStretch(1, 0)  # Header
        layout.setRowStretch(2, 2)  # Graph
        layout.setColumnStretch(0, 1)

        self.setCentralWidget(container)

    # -------------------------
    # Graph Generation
    # -------------------------
    def _save_graph_to_png(self, graph: Digraph, filename_prefix: str) -> str:
        tmp_dir = tempfile.gettempdir()
        path = os.path.join(tmp_dir, filename_prefix)
        graph.graph_attr['dpi'] = '300'
        graph.attr(size="10,10!")
        graph.render(path, format='png', cleanup=True)
        return path + ".png"

    def build_graphviz_graph(self, element_data):
        total_nodes = self._count_nodes(element_data)
        # Use dot for most graphs; fdp only if small-medium; avoid sfdp
        if total_nodes < 50:
            engine = "dot"
        else:
            engine = "neato"  # much more stable on Windows than fdp/sfdp
        graph = Digraph(engine=engine)
        graph.attr(
            rankdir="LR", splines="true", overlap="false",
            sep="+0.5", nodesep="0.5", ranksep="1.0", concentrate="false"
        )
        self._add_element_to_graph(graph, element_data)
        return graph

    def _add_element_to_graph(self, graph, element_data, parent_id=None):
        element_type = element_data.get("element_type", "Unknown")
        element_id = element_data.get("element_id", "")
        label = f"{element_type}\\n(ID: {element_id})" if element_id else element_type
        node_id = f"{element_type}_{id(element_data)}"

        graph.node(node_id, label=label, shape="box", style="rounded,filled",
                   fillcolor="#FFF9C4", color="#424242")

        if parent_id:
            graph.edge(parent_id, node_id, color="gray")

        with graph.subgraph(name=f"cluster_{node_id}") as sub:
            sub.attr(style="dashed", color="gray70", label="Properties")
            for prop in element_data.get("properties", []):
                prop_name = prop.get("feature_name", "unknown")
                val = prop.get("value")
                if isinstance(val, dict) and "element_type" in val:
                    self._add_element_to_graph(sub, val, node_id)
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict) and "element_type" in item:
                            self._add_element_to_graph(sub, item, node_id)
                        else:
                            prop_node_id = f"{node_id}_{prop_name}_{id(item)}"
                            sub.node(prop_node_id, f"{prop_name}: {item}", shape="note",
                                     color="#E0E0E0", fontcolor="#424242")
                            sub.edge(node_id, prop_node_id, color="#9E9E9E", style="dotted")
                else:
                    prop_node_id = f"{node_id}_{prop_name}"
                    text = f"{prop_name}: {val}" if val is not None else prop_name
                    sub.node(prop_node_id, text, shape="note", color="#E0E0E0", fontcolor="#424242")
                    sub.edge(node_id, prop_node_id, color="#9E9E9E", style="dotted")

    def _count_nodes(self, element_data):
        count = 1
        for prop in element_data.get("properties", []):
            val = prop.get("value")
            if isinstance(val, dict) and "element_type" in val:
                count += self._count_nodes(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict) and "element_type" in item:
                        count += self._count_nodes(item)
        return count

    # -------------------------
    # Utility
    # -------------------------
    def center_on_screen(self):
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
