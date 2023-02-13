import rnode
import util
from rnode import RNode


def all_test():
    print("--------Test begin-------")

    print("-------Matrix test-------")
    matrix_test()

    print("---Rnode creation test---")
    rnode_creation_test()

    print("---------Test end--------")


def matrix_test():
    a, b, c = util.make_matrix()

    print(a)
    print(b)
    print(c)


def rnode_creation_test():
    node1 = RNode(0, rnode.Op.MUL, "x", [], [])
    node2 = RNode(1, rnode.Op.MUL, "x_2", [], [])
    node3 = RNode(2, rnode.Op.MUL, "x_3", [], [])
    node1.print()
    node2.print()
    node3.print()

    node2.add_child(node3)
    node2.add_father(node1)
    node1.print()
    node2.print()
    node3.print()
