class Node:
    def __init__(self, value = 0.0):
        self.links = []
        self.value = value

    def __call__(self):
        if self.links:
            return sum([link() for link in self.links])
        return self.value

class Link:
    def __init__(self, input_node, output_node):
        self.weight = 1.0
        self.input_node = input_node
        output_node.links.append(self)

    def __call__(self):
        val = self.input_node()
        if val != 0:
            return self.weight * val
        return self.weight * self.input_node.value