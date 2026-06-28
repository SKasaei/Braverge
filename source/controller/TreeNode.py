

class TreeNode:

    def __init__(self, name):
            self.name = name
            self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    # def __init__(self, name, children=None):
    #     self.name = name
    #     self.children = children if children is not None else []

    def print_tree(self, node, level=0, indent_char="  "):
        print(f"{indent_char * level}- {node.name}")
        for child in node.children:
            self.print_tree(child, level + 1, indent_char)

    def get_name(self):
        return self.name
    
    def build_tree_string(self, node=None, level=0, indent_char="  "):
        if node is None:
            node = self
        result = f"{indent_char * level}- {node.name}\n"
        for child in node.children:
            result += self.build_tree_string(child, level + 1, indent_char)
        return result