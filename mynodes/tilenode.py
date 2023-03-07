from typing import List

from mynodes.rnode import *


def choose_tile(tile_list):
    quadratic: List[TileNode] = []
    linear: List[TileNode] = []
    tiles = None

    res: TileNode = None
    res_index = 0
    w: float = 0

    for tile in tile_list:
        if tile.is_quadratic():
            quadratic.append(tile)
        else:
            linear.append(tile)

    if len(quadratic) > 0:
        tiles = quadratic
    else:
        tiles = linear

    for tile in tiles:
        new_w = tile.weight()
        if new_w > w:
            res = tile
            w = new_w

    for i, tile in enumerate(tile_list):
        if tile.id == res.id:
            res_index = i
            break

    return res, res_index


class TileNode:

    def __init__(self, id, rnode: RNode, field=1, child=[], father=[]):
        self.id = id
        self.rnode: RNode = rnode
        self.field = field
        self.tile_child = child
        self.tile_father = father

    def __str__(self):
        return "Tile node created from " + str(self.rnode)

    @classmethod
    def create_tile_node_from_rnode(cls, rnode: RNode):
        node = TileNode(rnode.id, rnode)
        return node

    @classmethod
    def clear(cls):
        TileNode.tile_list = []
        print("Clear the tile list")

    def add_child(self, c):
        for node in self.tile_child:
            if c.id == node.id:
                return False

        self.tile_child.append(c)
        c.tile_father.append(self)
        return True

    def add_father(self, f):
        for node in self.tile_father:
            if f.id == node.id:
                return False

        self.tile_father.append(f)
        f.tile_child.append(self)
        return True

    def remove_child(self, c):
        for node in self.tile_child:
            if node.id == c.id:
                self.tile_child.remove(c)
                c.tile_father.remove(self)
                return True
        return False

    def remove_father(self, f):
        for node in self.tile_father:
            if node.id == f.id:
                self.tile_father.remove(f)
                f.tile_child.remove(self)
                return True
        return False

    # 仅保留tile_node的id和所对应rnode
    # 只在
    def fresh(self):
        for t in self.tile_child:
            t.fresh()
            del t

        self.field = 1
        self.tile_child = []
        self.tile_father = []

    def get_tile(self):
        self.__get_tile(True)

    def __get_tile(self, flag=False):
        self.fresh()

        if len(self.rnode.father) == 0:
            print("Tile node %d don't have fathers, end" % (self.id,))
            return self

        # 创建两个father的tile node
        l_father: TileNode = TileNode.create_tile_node_from_rnode(self.rnode.father[0])
        # print("Tile node %d's left father: %s" % (self.id, str(self.rnode.father[0])))

        r_father: TileNode = None
        if len(self.rnode.father) == 2:
            r_father = TileNode.create_tile_node_from_rnode(self.rnode.father[1])
            # print("Tile node %d's right father: %s" % (self.id, str(self.rnode.father[1])))
        else:
            r_father: TileNode = TileNode.create_tile_node_from_rnode(self.rnode.father[0])
            # print("Tile node %d's right father: %s" % (self.id, str(self.rnode.father[0])))

        # 　在线性约束的瓦片中遇到二次型,退出
        if not flag and (self.rnode.op == Op.MUL) and not (l_father.rnode.is_const()) and not (
                r_father.rnode.is_const()):
            print("CASE2, encounter quadratic piece in the linear tile, end")
            print("\tTile node %d * tile node %d = tile node %d" % (l_father.id, r_father.id, self.id))
            return self

        # CASE1: 二次约束的瓦片, 直接返回最简单的a*b=c
        if flag and (self.rnode.op == Op.MUL) and not (l_father.rnode.is_const()) and not (r_father.rnode.is_const()):
            self.add_father(l_father)
            self.add_father(r_father)

            print("CASE1, find a quadratic tile")
            print("\tTile node %d * tile node %d = tile node %d" % (l_father.id, r_father.id, self.id))

            return self

        # CASE2: 线性约束的瓦片

        # 本身为乘号, 那么左右父亲有一个为const
        if self.rnode.op == Op.MUL:
            # 左右均为const结点, const节点有后继一定无前驱
            if l_father.rnode.name == RNode.CONST_NAME and r_father.rnode.name == RNode.CONST_NAME:
                self.add_father(l_father)
                self.add_father(r_father)
                print("CASE2, %d * %d = tile node %d" % (r_father.rnode.const, l_father.rnode.const, self.id))
            elif l_father.rnode.name == RNode.CONST_NAME:
                self.add_father(l_father)
                self.add_father(r_father.__get_tile())
                print("CASE2, %d * tile node %d = tile node %d" % (l_father.rnode.const, r_father.id, self.id))
            else:
                self.add_father(l_father.__get_tile())
                self.add_father(r_father)
                print("CASE2, %d * tile node %d = tile node %d" % (r_father.rnode.const, l_father.id, self.id))

        # node为加法, 继续连加
        elif self.rnode.op == Op.ADD:
            print("Tile node %d's op is ADD, l_father: %d, r_father: %d" % (
                self.id, l_father.rnode.id, r_father.rnode.id))
            self.add_father(l_father.__get_tile())
            self.add_father(r_father.__get_tile())
            return self

        # node为最初的变量
        else:
            print("Tile node %d don't have fathers, end" % (self.id,))
            return self

    def show_tile(self):
        self.__show_tile(1)

    def __show_tile(self, layer=0):
        prefix = "\t" * layer
        print(prefix + str(self))

        for c in self.tile_father:
            c.__show_tile(layer + 1)

    def remove_tile_from_tree(self):

        for node in self.tile_father:
            node.remove_tile_from_tree()
            c_node = self.rnode
            f_node = node.rnode

            f_node.remove_child(c_node)

        self.fresh()

    def is_quadratic(self):

        if len(self.tile_father) == 0:
            return False
        elif len(self.tile_father) == 1:
            return self.rnode.op == Op.MUL and not self.rnode.father[0].is_const()
        else:
            return self.rnode.op == Op.MUL and not self.rnode.father[0].is_const() and not self.rnode.father[
                1].is_const()

    def weight(self) -> float:
        if len(self.tile_father) == 0:
            return self.rnode.weight
        elif len(self.tile_father) == 1:
            return self.rnode.weight + self.tile_father[0].weight()
        else:
            return self.rnode.weight + self.tile_father[0].weight() + self.tile_father[1].weight()