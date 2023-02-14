import util
import numpy as np
from rnode import *


def all_test():
    print("--------Test begin-------")

    print("-------Matrix test-------")
    matrix_test()

    print("---Rnode creation test---")
    rnode_creation_test()

    print("---Tree creation test----")
    tree_creation_test()

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
    a, b, c = util.make_matrix()

    node_num = len(a[0]) - 1
    constraint_num = len(a)

    print("node_num: %d, constrain_num: %d" % (node_num, constraint_num))

    # 创建约束中除了~one以外的变量的node
    for _ in range(node_num):
        RNode.new_node()

    for node in RNode.node_list:
        node.print()

    # 创建每一条约束
    for index in range(constraint_num):
        constraint_a = a[index]
        constraint_b = b[index]
        constraint_c = c[index]

        if len([i for i in constraint_c if i != 0]) == 1:

            # 该约束只是一个简单的乘法,由于预处理矩阵时满足任一限制的c组中一定存在一个field为1的变量,所以该c中的非零field一定为1
            if len([i for i in constraint_a if i != 0]) == 1 and len([i for i in constraint_b if i != 0]) == 1:
                node1 = None
                node2 = None
                node3 = None
                for i in range(node_num):
                    if constraint_a[i] != 0:
                        if i == 0:
                            node1 = RNode.new_const_node(constraint_a[0])
                        elif constraint_a[i]==1:
                            node1=RNode.node_list[i-1]
                        else:
                            node1 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_a[i]))
                    if constraint_b[i] != 0:
                        if i == 0:
                            node2 = RNode.new_const_node(constraint_b[0])
                        elif constraint_b[i] == 1:
                            node2 = RNode.node_list[i - 1]
                        else:
                            node2 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_b[i]))
                    if constraint_c[i] != 0:
                        if i == 0:
                            node3 = RNode.new_const_node(constraint_c[0])
                        elif constraint_c[i] == 1:
                            node3 = RNode.node_list[i - 1]
                        else:
                            node3 = RNode.node_list[i - 1]

                node1.add_child(node3)
                node2.add_child(node3)
                node3.add_father(node1)
                node3.add_father(node2)
                node3.op = Op.MUL

                for node in RNode.node_list:
                    node.print()

    return "yes"
