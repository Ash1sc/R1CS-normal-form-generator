from mynodes.tilenode import *
from mynodes.rnode import *
from typing import Dict

from functools import total_ordering


@total_ordering
class Tile_n_weight:
    def __init__(self, tile: TileNode = None, weight: float = 0):
        self.tile: TileNode = tile
        self.weight: float = weight

    def __eq__(self, other):
        return self.tile.id == other.tile.id

    def __gt__(self, other):
        # quadratic的瓦片永远大于linear的瓦片
        # if self.tile.is_quadratic() and not other.tile.is_quadratic():
        #     return True
        # elif not self.tile.is_quadratic() and other.tile.is_quadratic():
        #     return False
        # else:
        #     # 同种类型的瓦片,比较weight的大小
        #     return self.weight > other.weight

        # quadratic > linear with mul root >linear with add root
        self_level = 0
        other_level = 0
        if self.tile.is_quadratic():
            self_level = 3
        elif self.tile.rnode.op == Op.MUL:
            self_level = 2
        else:
            self_level = 1

        if other.tile.is_quadratic():
            other_level = 3
        elif other.tile.rnode.op == Op.MUL:
            other_level = 2
        else:
            other_level = 1

        if not self_level == other_level:
            return self_level > other_level
        else:
            return self.weight > other.weight


class Constraint:
    def __init__(self, size: float = 1):
        self.a = [0 for _ in range(size)]
        self.b = [0 for _ in range(size)]
        self.c = [0 for _ in range(size)]

    def get_size(self):
        return len(self.a)

    def resize(self, new_size):

        if self.get_size() > new_size:
            return False
        elif self.get_size() == new_size:
            return True
        else:
            for i in range(new_size - self.get_size()):
                self.a.append(0)
                self.b.append(0)
                self.c.append(0)

    def set_constraint(self, a_dict: Dict[int, int], b_dict: Dict[int, int], c_dict: Dict[int, int]):

        # dict是从列数到field
        for index, value in a_dict.items():
            self.a[index] = value
        for index, value in b_dict.items():
            self.b[index] = value
        for index, value in c_dict.items():
            self.c[index] = value

    def show(self):
        print("a: ", self.a)
        print("b: ", self.b)
        print("c: ", self.c)


class Consgen:

    def __init__(self, tile_list, weight_list):
        self.tw_list: List[Tile_n_weight] = []
        self.cons_list: List[Constraint] = []

        # 0预留给~one变量
        self.current_index = 1

        # node id 到 矩阵中的列数
        self.dict = dict()

        for index, _ in enumerate(tile_list):
            self.tw_list.append(Tile_n_weight(tile_list[index], weight_list[index]))

        self.tw_list.sort(reverse=True)

    def __get_index(self, id):

        # 如果是~one, 那么返回0
        if RNode.node_list[id].is_const():
            return 0

        # dict中已有, 那么选择已有
        if id in self.dict:
            return self.dict[id]
        else:
            # dict中无, 为其分配最新的index
            self.dict[id] = self.current_index
            self.current_index += 1
            return self.dict[id]

    def __add_constraint(self, a_dict: Dict[int, int], b_dict: Dict[int, int], c_dict: Dict[int, int]):

        for cons in self.cons_list:
            cons.resize(self.current_index)

        new_con = Constraint(self.current_index)
        new_con.set_constraint(a_dict, b_dict, c_dict)
        self.cons_list.append(new_con)

    def __get_mul_linear_dict(self, tile):
        field = 1
        node_id = 0

        target = tile
        while not len(target.tile_father) == 0:
            l_father = target.tile_father[0]
            r_father = target.tile_father[1]

            if l_father.rnode.is_const() and not r_father.rnode.is_const():
                field = field * l_father.rnode.const
                node_id = r_father.rnode.id
                target = r_father
            elif r_father.rnode.is_const() and not l_father.rnode.is_const():
                field = field * r_father.rnode.const
                node_id = l_father.rnode.id
                target = l_father
            else:
                field = field * l_father.rnode.const * r_father.rnode.const
                node_id = 0
                break

        val_id = node_id
        res_id = tile.rnode.id

        return field, val_id, res_id

    def __get_add_linear_field_dict(self, tile):

        res = dict()
        stack = [tile]
        const = 0
        while len(stack) != 0:
            tile_node = stack.pop()

            print("Tile id: %d" % (tile_node.id,))

            # 根节点,自身field为-1
            if tile_node.id == tile.id:
                res[tile_node.id] = -1

            # Op = ADD
            # 中间节点, 将父节点添加至stack
            if tile_node.rnode.op == Op.ADD:

                print("\tTile node id %d, op is ADD" % (tile_node.id,))
                for f in tile_node.tile_father:
                    stack.append(f)
                    print("\t\tAdd father tile node id %d to the stack" % (f.id,))

            # Op = MUL
            elif tile_node.rnode.op == Op.MUL:
                if len(tile_node.tile_father) != 0:
                    field, val_id, res_id = self.__get_mul_linear_dict(tile_node)
                    if not val_id in res:
                        res[val_id] = field
                    else:
                        res[val_id] = field + res[val_id]

                    print("\tTile node id %d, op is MUL, created by const mul list" % (tile_node.id,))
                    print("\tSet node %id's field to %d" % (val_id, res[val_id]))

                else:
                    if not tile_node.id in res:
                        res[tile_node.id] = 1
                    else:
                        res[tile_node.id] = 1 + res[tile_node.id]
                        print("\tTile node id %d, op is MUL, created by quadratic tile" % (tile_node.id,))
                        print("\tSet node %id's field to %d" % (tile_node.id, res[tile_node.id]))


            # Op = None
            # 常数节点, 通通加到index=0
            elif tile_node.rnode.is_const():

                const += tile_node.rnode.const

                print("\tTile node id %d, is const" % (tile_node.id,))
                print("\tSet const field to %d" % (const, ))

            # 　无父结点，将自身的 field + 1
            elif len(tile_node.tile_father) == 0:
                if not tile_node.id in res:
                    res[tile_node.id] = 1
                else:
                    res[tile_node.id] = 1 + res[tile_node.id]

                print("\tTile node id %d, is variable" % (tile_node.id,))
                print("\tSet node %d's field to %d" % (tile_node.id, res[tile_node.id]))

        return res, const

    def cons_generation(self):

        for tw in self.tw_list:
            tw.tile.show_tile()
            print("\tweight: ", tw.weight)

        for tw in self.tw_list:
            tile = tw.tile

            # quadratic 直接利用
            # quadratic 一定是1,1,1的field
            if tile.is_quadratic():
                child_id = tile.id
                lf_id = tile.tile_father[0].id
                rf_id = tile.tile_father[0].id
                if len(tile.tile_father) >= 2:
                    rf_id = tile.tile_father[1].id

                # print("lf_id: %d, rf_id: %d, child_id:%d" % (lf_id, rf_id, child_id))

                # 确保betweeness 大的父节点一定在约束组中的位置更加前面
                if lf_id != rf_id and tile.tile_father[0] > tile.tile_father[1]:
                    # print("lf betweeness: %d, rf betweeness: %d" % (
                    # tile.tile_father[0].betweeness(), tile.tile_father[1].betweeness()))
                    lf_index = self.__get_index(lf_id)
                    rf_index = self.__get_index(rf_id)
                    child_index = self.__get_index(child_id)
                else:
                    # if lf_id != rf_id:
                    # print("lf betweeness: %d, rf betweeness: %d" % (
                    # tile.tile_father[0].betweeness(), tile.tile_father[1].betweeness()))
                    rf_index = self.__get_index(rf_id)
                    lf_index = self.__get_index(lf_id)
                    child_index = self.__get_index(child_id)

                # print("lf_index: %d, rf_index: %d, child_index:%d" % (lf_index, rf_index, child_index))

                a_dict = dict()
                b_dict = dict()
                c_dict = dict()

                c_dict[child_index] = 1
                if lf_index < rf_index:
                    a_dict[lf_index] = 1
                    b_dict[rf_index] = 1
                else:
                    a_dict[rf_index] = 1
                    b_dict[lf_index] = 1

                self.__add_constraint(a_dict, b_dict, c_dict)

            else:
                print("oops!This is a linear constraint")

                # tile: (*) - 4
                #           \ (*) - 5
                #                 \ (*) - 3
                #                       \ 4
                if tile.rnode.op == Op.MUL:
                    field, val_id, res_id = self.__get_mul_linear_dict(tile)

                    a_dict = dict()
                    b_dict = dict()
                    c_dict = dict()

                    val_index = self.__get_index(val_id)
                    res_index = self.__get_index(res_id)

                    a_dict[0] = field
                    b_dict[val_index] = 1
                    c_dict[res_index] = 1

                    self.__add_constraint(a_dict, b_dict, c_dict)

                else:
                    # node id 到 field 的dict
                    field_dict, const = self.__get_add_linear_field_dict(tile)

                    print(field_dict, const)

                    a_dict = dict()
                    b_dict = dict()
                    c_dict = dict()
                    for key, value in field_dict.items():
                        index = self.__get_index(key)
                        a_dict[index] = value
                    a_dict[0] = const

                    b_dict[0] = 1

                    self.__add_constraint(a_dict, b_dict, c_dict)

        for cons in self.cons_list:
            cons.show()

        return self.cons_list
