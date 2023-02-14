import util
from rnode import *


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
    node1 = RNode.new_node(Op.MUL, "x")
    node2 = RNode.new_node(Op.MUL, "x_2")
    node3 = RNode.new_node(Op.MUL, "x_3")
    for node in RNode.node_list:
        node.print()

    node2.add_child(node3)
    node2.add_father(node1)
    for node in RNode.node_list:
        node.print()

    RNode.clear()
    for node in RNode.node_list:
        node.print()


def tree_creation_test():
    return "yes"