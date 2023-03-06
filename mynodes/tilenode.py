from rnode import *


class TileNode:
    tile_list = []

    def __init__(self, id, rnode:RNode, field=1, child=[], father=[]):
        self.id = id
        self.rnode = rnode
        self.field = field
        self.tile_child = child
        self.tile_father = father

    @classmethod
    def create_ile_node_from_rnode(cls, rnode:RNode):
        node = TileNode(rnode.id, rnode)
        return node

    @classmethod
    def clear(cls):
        TileNode.tile_list = []
        print("Clear the tile list")

    def add_child(self, c:RNode):
        for node in self.tile_child:
            if c.id == node.id:
                return False

        self.tile_child.append(c)
        c.tile_father.append(self)
        return True

    def add_father(self, f: RNode):
        for node in self.tile_father:
            if f.id == node.id:
                return False

        self.tile_father.append(f)
        f.tile_child.append(self)
        return True

    def remove_child(self, c: RNode):
        for node in self.child:
            if node.id == c.id:
                self.tile_child.remove(c)
                c.tile_father.remove(self)
                return True
        return False

    def remove_father(self, f: RNode):
        for node in self.father:
            if node.id == f.id:
                self.father.remove(f)
                f.child.remove(self)
                return True
        return False
