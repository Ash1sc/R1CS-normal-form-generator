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
    var_num = len(a[0])
    constraint_num = len(a)

    print("node_num: %d, constrain_num: %d" % (node_num, constraint_num))

    # 创建约束中除了~one以外的变量的node
    for _ in range(node_num):
        RNode.new_node()

    for node in RNode.node_list:
        node.print()

    # 创建每一条约束
    for index in range(constraint_num):

        print("constraint: ", index)
        constraint_a = a[index]
        constraint_b = b[index]
        constraint_c = c[index]

        if len([i for i in constraint_c if i != 0]) == 1:

            # CASE 1: ab单一,c单一
            # 该约束只是一个简单的乘法,由于预处理矩阵时满足任一限制的c组中一定存在一个field为1的变量,所以该c中的非零field一定为1
            if len([i for i in constraint_a if i != 0]) == 1 and len([i for i in constraint_b if i != 0]) == 1:
                node1 = None
                node2 = None
                node3 = None

                # 依次遍历矩阵中的node, 找出三个矩阵向量中field的非零部分
                for i in range(var_num):
                    if constraint_a[i] != 0:

                        # 如果是~one变量, 那么创建const node
                        if i == 0:
                            node1 = RNode.new_const_node(constraint_a[0])
                            print("\tCASE1, add a const node as node1, value: %d" % (constraint_a[0],))

                        # 如果field为1, 直接取node_list中的node
                        elif constraint_a[i] == 1:
                            node1 = RNode.node_list[i - 1]
                            print("\tCASE1, choose an existing node as node1, id: %d" % (i - 1,))

                        # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                        else:
                            node1 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_a[i]))
                            print("\tCASE1, mul const node with an existing node as node1, id: %d" % (node1.id,))

                    if constraint_b[i] != 0:
                        if i == 0:
                            node2 = RNode.new_const_node(constraint_b[0])
                            print("\tCASE1, add a const node as node2, value: %d" % (constraint_b[0],))
                        elif constraint_b[i] == 1:
                            node2 = RNode.node_list[i - 1]
                            print("\tCASE1, choose an existing node as node2, id: %d" % (i - 1,))
                        else:
                            node2 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_b[i]))
                            print("\tCASE1, mul const node with an existing node as node2, id: %d" % (node2.id,))
                    if constraint_c[i] != 0:
                        if i == 0:
                            node3 = RNode.new_const_node(constraint_c[0])
                            print("\tCASE1, add a const node as node3, value: %d" % (constraint_c[0],))

                        # c中的非零field一定为1,所以一定可以直接取node list中的node
                        else:
                            node3 = RNode.node_list[i - 1]
                            print("\tCASE1, choose an existing node as node3, id: %d" % (i - 1,))

                node1.add_child(node3)
                node2.add_child(node3)
                node3.add_father(node1)
                node3.add_father(node2)
                node3.op = Op.MUL

            # CASE 2: ab不单一,c单一
            # a与b中是一个乘法分配律, c中是一个单纯的结果且field为1
            else:
                node1 = None
                node2 = None
                node1_flag = False
                node2_flag = False
                node_left = None
                node_right = None
                last_a = -1
                last_b = -1

                # 得到分配律中最后一项的下标
                for i in range(var_num):
                    if constraint_a[var_num - 1 - i] != 0:
                        last_a = var_num - 1 - i
                        break

                for i in range(var_num):
                    if constraint_b[var_num - 1 - i] != 0:
                        last_b = var_num - 1 - i
                        break

                print("\tCASE2, last_a: %d, last_b: %d" % (last_a, last_b))

                for i_a in range(var_num):

                    node1_flag = False
                    node1 = None
                    # 创建node1
                    if constraint_a[i_a] != 0:

                        # 如果是~one变量, 那么创建const node
                        if i_a == 0 and constraint_a[0] == 1:
                            node1_flag = True
                        elif i_a == 0 and constraint_a[0] != 1:
                            node1 = RNode.new_const_node(constraint_a[0])
                            print("\tCASE2, add a const node as node1, value: %d, id: %d" % (constraint_a[0], node1.id))

                        # 如果field为1, 直接取node_list中的node
                        elif constraint_a[i_a] == 1:
                            node1 = RNode.node_list[i_a - 1]
                            print("\tCASE2, choose an existing node as node1, id: %d" % (node1.id,))

                        # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                        else:
                            node1 = RNode.node_list[i_a - 1].mul(RNode.new_const_node(constraint_a[i_a]))
                            print("\tCASE2, mul const node with an existing node as node1, id: %d" % (node1.id,))

                        for i_b in range(var_num):

                            # 创建node2
                            node2_flag = False
                            node2 = None

                            if constraint_b[i_b] != 0:

                                # 如果是~one变量, 那么创建const node
                                if i_b == 0 and constraint_b[0] == 1:
                                    node2_flag = True

                                elif i_b == 0 and constraint_b[0] != 1:
                                    node2 = RNode.new_const_node(constraint_b[0])
                                    print("\t\tCASE2, add a const node as node2, value: %d, id: %d" % (
                                        constraint_b[0], node2.id))

                                # 如果field为1, 直接取node_list中的node
                                elif constraint_b[i_b] == 1:
                                    node2 = RNode.node_list[i_b - 1]
                                    print("\t\tCASE2, choose an existing node as node2, id: %d" % (node2.id,))

                                # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                                else:
                                    node2 = RNode.node_list[i_b - 1].mul(RNode.new_const_node(constraint_b[i_b]))
                                    print(
                                        "\t\tCASE2, mul const node with an existing node as node2, id: %d" % (
                                            node2.id,))

                                # 分配律到达最后一项
                                if i_a == last_a and i_b == last_b:
                                    print(
                                        "\t\tCASE2, last step at last_a: %d, last_b: %d, node3 + node_left = node_right" % (
                                            last_a, last_b))
                                    # 创建node3
                                    for i in range(var_num):
                                        if constraint_c[i] != 0:
                                            if i == 0:
                                                node_right = RNode.new_const_node(constraint_c[0])
                                                print("\t\tCASE2, add a const node as node_right, value: %d, id: %d" % (
                                                    constraint_c[0], node_right.id))
                                            else:
                                                node_right = RNode.node_list[i - 1]
                                                print(
                                                    "\t\tCASE2, choose an existing node as node_right, id: %d" % (
                                                        node_right.id,))

                                    if node1 is None or (node1.is_const() and node1.const == 1):
                                        if node2_flag:
                                            node2 = RNode.new_const_node(1)
                                        node3 = node2
                                        print(
                                            "\t\tCASE2, choose node2 as node3, node3 id: %d " % (
                                                node3.id,))
                                    elif node2 is None or (node2.is_const() and node2.const == 1):
                                        if node1_flag:
                                            node1 = RNode.new_const_node(1)
                                        node3 = node1
                                        print(
                                            "\t\tCASE2, choose node1 as node3, node3 id: %d" % (
                                                node3.id))

                                    else:
                                        node3 = node1.mul(node2)
                                        print("\t\tCASE2, node3 id: %d, node1 id: %d. node2 id: %d" % (
                                            node3.id, node1.id, node2.id))

                                    node_right.op = Op.ADD

                                    node_right.add_father(node_left)
                                    node_right.add_father(node3)
                                    node_left.add_child(node_right)
                                    node3.add_child(node_right)
                                    break
                                else:
                                    if node_left is None:
                                        if node1 is None or (node1.is_const() and node1.const == 1):
                                            if node2_flag:
                                                node2 = RNode.new_const_node(1)
                                            node_left = node2
                                            print(
                                                "\t\tCASE2, node_left is None, choose node2 as node_left, node_left id: %d " % (
                                                    node_left.id,))
                                        elif node2 is None or (node2.is_const() and node2.const == 1):
                                            if node1_flag:
                                                node1 = RNode.new_const_node(1)
                                            node_left = node1
                                            print(
                                                "\t\tCASE2, node_left is None, choose node1 as node_left, node_left id: %d" % (
                                                    node_left.id))
                                        else:
                                            node_left = node1.mul(node2)
                                            print("\t\tCASE2, node_left is None, id: %d, node1 id: %d. node2 id: %d" % (
                                                node_left.id, node1.id, node2.id))
                                    else:
                                        if node1.is_const() and node1.const == 1:
                                            node_left = node_left.add(node2)
                                            print(
                                                "\t\tCASE2, add node2 to node_left, node2 id: %d, node_left id: %d" % (
                                                    node2.id, node_left.id,))
                                        elif node2.is_const() and node2.const == 1:
                                            node_left = node_left.add(node1)
                                            print(
                                                "\t\tCASE2, add node1 to node_left, node1 id: %d, node_left id: %d" % (
                                                    node1.id, node_left.id))
                                        else:
                                            node_left = node_left.add(node1.mul(node2))
                                            print("\t\tCASE2, add to node_left, id: %d, node1 id: %d. node2 id: %d" % (
                                                node_left.id, node1.id, node2.id))
        else:
            # CASE 3: ab单一,c不单一
            # 该约束c中有多于一个field不为0, 但是a与b中只有一个field为非0
            if len([i for i in constraint_a if i != 0]) == 1 and len([i for i in constraint_b if i != 0]) == 1:
                node1 = None
                node2 = None
                node_left = None

                # 创建node1*node2=node3
                for i in range(var_num):
                    if constraint_a[i] != 0:

                        # 如果是~one变量, 那么创建const node
                        if i == 0:
                            node1 = RNode.new_const_node(constraint_a[0])

                        # 如果field为1, 直接取node_list中的node
                        elif constraint_a[i] == 1:
                            node1 = RNode.node_list[i - 1]

                        # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                        else:
                            node1 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_a[i]))
                    if constraint_b[i] != 0:
                        if i == 0:
                            node2 = RNode.new_const_node(constraint_b[0])
                        elif constraint_b[i] == 1:
                            node2 = RNode.node_list[i - 1]
                        else:
                            node2 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_b[i]))

                node_left = node1.mul(node2)

                # 创建node_right=-field1-field2
                node_right = None
                node3_index = -1
                node3 = None
                node4 = None
                for i in range(var_num):
                    if constraint_c[i] == 1:
                        node3_index = i
                        break

                for i in range(var_num):
                    if constraint_c[i] != 0 and i != node3_index:

                        # 构造node4
                        # 如果是~one变量, 那么创建const node
                        if i == 0:
                            node4 = RNode.new_const_node(0 - constraint_c[0])
                        elif constraint_c[i] == -1:
                            node4 = RNode.node_list[i - 1]
                        else:
                            node4 = RNode.node_list[i - 1].mul(RNode.new_const_node(0 - constraint_c[i]))

                        if node_right is None:
                            node_right = node4
                        else:
                            node_right = node_right.add(node4)

                node3 = RNode.node_list[node3_index - 1]

                node3.op = Op.ADD
                node3.add_father(node_right)
                node3.add_father(node_left)
                node_left.add_child(node3)
                node_right.add_child(node3)

            # CASE 4: ab不单一,c不单一
            # a与b中是一个乘法分配律, c中存在多个field不为0的情况
            else:
                node1 = None
                node2 = None
                node_left = None

                for i_a in range(var_num):

                    # 创建node1
                    if constraint_a[i_a] != 0:
                        print("build node1 at index: ", i_a)
                        # 如果是~one变量, 那么创建const node
                        if i_a == 0:
                            node1 = RNode.new_const_node(constraint_a[0])

                        # 如果field为1, 直接取node_list中的node
                        elif constraint_a[i_a] == 1:
                            node1 = RNode.node_list[i_a - 1]

                        # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                        else:
                            node1 = RNode.node_list[i_a - 1].mul(RNode.new_const_node(constraint_a[i_a]))

                        for i_b in range(var_num):
                            # 创建node2
                            if constraint_b[i_b] != 0:
                                print("\tbuild node2 at index: ", i_b)
                                # 如果是~one变量, 那么创建const node
                                if i_b == 0:
                                    node2 = RNode.new_const_node(constraint_b[0])

                                # 如果field为1, 直接取node_list中的node
                                elif constraint_b[i_b] == 1:
                                    node2 = RNode.node_list[i_b - 1]

                                # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                                else:
                                    node2 = RNode.node_list[i_b - 1].mul(RNode.new_const_node(constraint_b[i_b]))

                                if node_left is None:
                                    node_left = node1.mul(node2)
                                else:
                                    node_left = node_left.add(node1.mul(node2))

                # 创建node_right=-field1-field2
                node_right = None
                node3_index = -1
                node3 = None
                node4 = None
                for i in range(var_num):
                    if constraint_c[i] == 1:
                        node3_index = i
                        break

                for i in range(var_num):
                    if constraint_c[i] != 0 and i != node3_index:

                        # 构造node4
                        # 如果是~one变量, 那么创建const node
                        if i == 0:
                            node4 = RNode.new_const_node(0 - constraint_c[0])
                        elif constraint_c[i] == -1:
                            node4 = RNode.node_list[i - 1]
                        else:
                            node4 = RNode.node_list[i - 1].mul(RNode.new_const_node(0 - constraint_c[i]))

                        if node_right is None:
                            node_right = node4
                        else:
                            node_right = node_right.add(node4)

                node3 = RNode.node_list[node3_index - 1]

                node3.op = Op.ADD
                node3.add_father(node_right)
                node3.add_father(node_left)
                node_left.add_child(node3)
                node_right.add_child(node3)

        for node in RNode.node_list:
            node.print()

    return RNode.node_list
