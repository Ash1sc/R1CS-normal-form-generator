from mynodes.tilenode import *
from mynodes.rnode import *
from typing import Dict

from functools import total_ordering


@total_ordering
class Index_and_weight:
    def __init__(self, index=0, weight=0, usage=0):
        self.index: float = index
        self.weight: float = weight
        self.usage = usage

    def __gt__(self, other):
        return self.usage > other.usage or (self.usage == other.usage and self.weight > other.weight)

    def __eq__(self, other):
        return self.weight == other.weight


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

    def swap_row(self, i, j):
        tmp = self.a[i]
        self.a[i] = self.a[j]
        self.a[j] = tmp

        tmp = self.b[i]
        self.b[i] = self.b[j]
        self.b[j] = tmp

        tmp = self.c[i]
        self.c[i] = self.c[j]
        self.c[j] = tmp

    def set_row(self, i, j):
        self.a[i] = self.a[j]
        self.b[i] = self.b[j]
        self.c[i] = self.c[j]


class Consgen:

    def __init__(self, tile_list, weight_list):
        self.tw_list: List[Tile_n_weight] = []
        self.cons_list: List[Constraint] = []

        # 0预留给~one变量
        self.current_index = 1

        # quadratic constraint中使用的变量在矩阵中的最大的index
        self.__max_q_index = -1

        # quadratic constraint在矩阵中最大的index
        self.__q_cons_num = -1
        self.cons_num = 0

        # node id 到 矩阵中的列数
        self.dict = dict()

        for index, _ in enumerate(tile_list):
            self.tw_list.append(Tile_n_weight(tile_list[index], weight_list[index]))

        self.tw_list.sort(reverse=True)

    def __constraint_length(self):
        if self.cons_num == 0:
            return 0
        else:
            return len(self.cons_list[0].a)

    def __quick_sort(self, cons_index, iw: List[Index_and_weight], i, j):
        if i >= j:
            return list
        pivot = Index_and_weight(iw[i].index, iw[i].weight, iw[i].usage)

        low = i
        high = j
        while i < j:
            while i < j and \
                    (iw[j] > pivot or self.cons_list[cons_index].a[iw[j].index] > self.cons_list[cons_index].a[
                        pivot.index]):
                j -= 1
            iw[i] = iw[j]
            self.__set_row(i, j)
            while i < j and \
                    (iw[j] < pivot or self.cons_list[cons_index].a[iw[j].index] < self.cons_list[cons_index].a[
                        pivot.index]):
                i += 1
            iw[j] = iw[i]
            self.__set_row(j, i)
        iw[j] = pivot
        self.cons_list[j] = pivot
        self.__quick_sort(iw, low, i - 1)
        self.__quick_sort(iw, i + 1, high)

    def __swap_row(self, i, j):

        index = self.dict[i]
        self.dict[i] = self.dict[j]
        self.dict[j] = self.dict[i]

        for cons in self.cons_list:
            cons.swap_row(i, j)

    def __set_row(self, i, j):

        self.dict[i] = self.dict[j]

        for cons in self.cons_list:
            cons.set_row(i, j)

    def __swap_line(self, i, j):
        tmp = self.cons_list[i]
        self.cons_list[i] = self.cons_list[j]
        self.cons_list[j] = tmp

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

        self.cons_num += 1

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
            # 根节点,自身field为-1
            if tile_node.id == tile.id and not tile_node.rnode.is_const():
                res[tile_node.id] = -1
            elif tile_node.id == tile.id and not tile_node.rnode.is_const():
                const = -1

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
                print("\tSet const field to %d" % (const,))

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

                self.__q_cons_num += 1

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

                # 记录max_q_index, 对max_q_index两边的row,即在quadratic和linear中出现的节点分别进行排序
                self.__max_q_index = max(rf_index, lf_index, child_index, self.__max_q_index)

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

        # 调整linear constraint中的列数顺序
        start_index = self.__max_q_index + 1
        end_index = len(self.cons_list[0].a) - 1

        # 计算linear constraint中新增变量的weight = Σ(field * tile weight)
        iw_list: List[Index_and_weight] = []

        # quadratic 顶点占位
        for i in range(self.__max_q_index + 1):
            iw_list.append(Index_and_weight())

        for cur_index in range(start_index, end_index + 1):
            weight = 0
            usage = 0
            for cons_index in range(self.__q_cons_num + 1, self.cons_num):
                weight = weight + np.abs((self.cons_list[cons_index].a[cur_index] + self.cons_list[cons_index].b[cur_index] +
                                   self.cons_list[cons_index].c[cur_index]) * self.tw_list[cons_index].weight)
                # if self.cons_list[cons_index].a[cur_index] != 0:
                #     usage += 1
                # if self.cons_list[cons_index].b[cur_index] != 0:
                #     usage += 1
                # if self.cons_list[cons_index].c[cur_index] != 0:
                #     usage += 1

            iw_list.append(Index_and_weight(cur_index, weight, usage))
        # 对每一个linear constraint中的新增节点进行单独的排序
        i = self.__max_q_index + 1
        j = i
        for cons_index in range(self.__q_cons_num + 1, self.cons_num):

            if i >= self.__constraint_length():
                break

            while j < self.__constraint_length() and self.cons_list[cons_index].a[j] != 0:
                j = j + 1

            # 减去自己的field *　weight
            for val_index in range(i, j):
                iw_list[val_index].weight-=np.abs(self.cons_list[cons_index].a[val_index] * self.tw_list[cons_index].weight)
            self.__quick_sort(cons_index, iw_list, i, j - 1)

            i = j

        # 调整quadratic constraint中的列数顺序
        start_index = 0
        end_index = self.__max_q_index

        for cons in self.cons_list:
            cons.show()

        return self.cons_list
