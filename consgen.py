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
        if self.tile.is_quadratic() and not other.tile.is_quadratic():
            return True
        elif not self.tile.is_quadratic() and other.tile.is_quadratic():
            return False
        else:
            # 同种类型的瓦片,比较weight的大小
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

                print("%d, %d, %d" % (child_id, lf_id, rf_id))
                rf_index = self.__get_index(rf_id)
                lf_index = self.__get_index(lf_id)
                child_index = self.__get_index(child_id)

                print(print("lf_index: %d, rf_index: %d, child_index:%d" % (child_index, lf_index, rf_index)))

                a_dict = dict()
                b_dict = dict()
                c_dict = dict()

                c_dict[child_index] = 1

                if rf_index < lf_index:
                    a_dict[rf_index] = 1
                    b_dict[lf_index] = 1
                else:
                    b_dict[rf_index] = 1
                    a_dict[lf_index] = 1

                self.__add_constraint(a_dict, b_dict, c_dict)

        for cons in self.cons_list:
            cons.show()

        return self.cons_list
