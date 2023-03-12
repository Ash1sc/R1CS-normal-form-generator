from mynodes.tilenode import *
from mynodes.rnode import *

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
        if self.tile.is_quadratic() and not other.tile.is_quodratic():
            return True
        elif not self.tile.is_quadratic() and other.tile.is_quodratic():
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


class Consgen:

    def __init__(self, tile_list, weight_list):
        self.tw_list: List[Tile_n_weight] = [Tile_n_weight() for _ in len(tile_list)]
        self.cons_list: List[Constraint] = []

        for index, _ in tile_list:
            self.tw_list[index] = Tile_n_weight(tile_list[index], weight_list[index])

    def cons_generation(self):
        return self.cons_list
