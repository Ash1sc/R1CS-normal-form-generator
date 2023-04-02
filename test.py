from typing import List

import util
import pagerank as pr
from mynodes.rnode import *
from mynodes.tilenode import *
from consgen import *

from weight_calculator import *


def all_test():
    print("\n\n--------Test begin-------")

    print("\n\n-------Matrix test-------\n\n")
    matrix_test()

    print("\n\n---Rnode creation test---\n\n")
    rnode_creation_test()

    print("\n\n---Tree creation test----\n\n")
    tree_creation_test()

    print("\n\n----Node weight test-----\n\n")
    node_weight_test()

    print("\n\n----Cover type-1 test----\n\n")
    tiles = cover_algorithm_1_test()

    print("\n\n----Tile weight test-----\n\n")
    tile_weight = tile_weight_calc(tiles)

    print("\n\n----Cons generation test-----\n\n")
    constraint_generation(tiles, tile_weight)

    print("\n\n---------Test end--------\n\n")


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

    RNode.node_list.remove(node2)
    for node in RNode.node_list:
        node.print()

    RNode.clear()
    for node in RNode.node_list:
        node.print()


# field * var 改为 const node * var node
# const node 每次均为新建,所以const node 不会同时存在前驱与后继节点
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
                            print("\tCASE1, add a const node as node1, value: %f" % (constraint_a[0],))

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
                            print("\tCASE1, add a const node as node2, value: %f" % (constraint_b[0],))
                        elif constraint_b[i] == 1:
                            node2 = RNode.node_list[i - 1]
                            print("\tCASE1, choose an existing node as node2, id: %d" % (i - 1,))
                        else:
                            node2 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_b[i]))
                            print("\tCASE1, mul const node with an existing node as node2, id: %d" % (node2.id,))
                    if constraint_c[i] != 0:
                        if i == 0:
                            node3 = RNode.new_const_node(constraint_c[0])
                            print("\tCASE1, add a const node as node3, value: %f" % (constraint_c[0],))

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
                            print("\tCASE2, add a const node as node1, value: %f, id: %d" % (constraint_a[0], node1.id))

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
                                    print("\t\tCASE2, add a const node as node2, value: %f, id: %d" % (
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
                                                print("\t\tCASE2, add a const node as node_right, value: %f, id: %d" % (
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

                node1_flag = False
                node2_flag = True

                # 创建node1*node2=node_left
                for i in range(var_num):
                    if constraint_a[i] != 0:

                        # 如果是~one变量并且不为1, 那么创建const node
                        if i == 0 and constraint_a[0] != 1:
                            node1 = RNode.new_const_node(constraint_a[0])

                        # 是~one变量且为1, 可能可以不用创建
                        elif i == 0 and constraint_a[0] == 1:
                            node1_flag = True

                        # 如果field为1, 直接取node_list中的node
                        elif constraint_a[i] == 1:
                            node1 = RNode.node_list[i - 1]

                        # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                        else:
                            node1 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_a[i]))
                    if constraint_b[i] != 0:
                        if i == 0 and constraint_b[0] != 1:
                            node2 = RNode.new_const_node(constraint_b[0])
                        elif i == 0 and constraint_b[0] == 1:
                            node2_flag = True
                        elif constraint_b[i] == 1:
                            node2 = RNode.node_list[i - 1]
                        else:
                            node2 = RNode.node_list[i - 1].mul(RNode.new_const_node(constraint_b[i]))

                if node1 is None or (node1.is_const() and node1.const == 1):
                    if node2_flag:
                        node2 = RNode.new_const_node(1)
                        node_left = node2
                        print("\tCASE3, choose node2 as node_left, node_left id: %d " % (node_left.id,))


                elif node2 is None or (node2.is_const() and node1.const == 1):
                    if node1_flag:
                        node1 = RNode.new_const_node(1)
                        node_left = node1
                        print("\tCASE3, choose node1 as node_left, node_left id: %d " % (node_left.id,))

                else:
                    node_left = node1.mul(node2)
                    print(
                        "\tCASE3, node_left id: %d, node1 id: %d. node2 id: %d" % (node_left.id, node1.id, node2.id))

                # 创建node_right-field1-field2=node3
                node_right = None
                node3_index = -1
                last_index = -1
                node3 = None
                node4 = None

                # 找到第一位field为1的变量
                for i in range(var_num):
                    if constraint_c[i] == 1:
                        node3_index = i
                        print("\tCASE3, find node3, node3 id: %d" % (node3_index - 1,))
                        break

                # 找到c中最后一个不为0的field的下标
                for i in range(var_num):
                    index = var_num - i - 1
                    if index == node3_index:
                        continue
                    elif constraint_c[index] != 0:
                        last_index = index
                        print("\tCASE3, find last node in the add list, node id: %d" % (last_index - 1,))
                        break

                for i in range(var_num):
                    if constraint_c[i] != 0 and i != node3_index and i != last_index:

                        # 构造node4
                        # 如果是~one变量, 那么创建const node
                        if i == 0:
                            node4 = RNode.new_const_node(0 - constraint_c[0])
                        elif constraint_c[i] == -1:
                            node4 = RNode.node_list[i - 1]
                        else:
                            node4 = RNode.node_list[i - 1].mul(RNode.new_const_node(0 - constraint_c[i]))

                        old_node_left_id = node_left.id
                        node_left = node_left.add(node4)
                        print("\tCASE3, add node4 to node_left, new id: %d, old id: %d, node4 id: %d" % (
                            node_left.id, old_node_left_id, node4.id))

                        # if node_right is None:
                        #     node_right = node4
                        #     print("\tCASE3, node_right is None, choose node4, node 4 id: %d" % (node4.id,))
                        # else:
                        #     old_node_right_id = node_right.id
                        #     node_right = node_right.add(node4)
                        #     print("\tCASE3, add node4 to node_right, new id: %d, old id: %d, node4 id: %d" % (
                        #         node_right.id, old_node_right_id, node4.id))

                    # 利用最后一个node构建node_right
                    elif constraint_c[i] != 0 and i != node3_index and i == last_index:
                        if i == 0:
                            node_right = RNode.new_const_node(0 - constraint_c[0])
                        elif constraint_c[i] == -1:
                            node_right = RNode.node_list[i - 1]
                        else:
                            node_right = RNode.node_list[i - 1].mul(RNode.new_const_node(0 - constraint_c[i]))

                if node3_index == 0:
                    node3 = RNode.new_const_node(1)
                else:
                    node3 = RNode.node_list[node3_index - 1]

                print("\tCASE3, node_left+node_right=node3, left id: %d, right id: %d, node3 id: %d" % (
                    node_left.id, node_right.id, node3.id))

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
                node1_flag = False
                node2_flag = False

                node_left = None

                for i_a in range(var_num):

                    node1 = None
                    node1_flag = False

                    # 创建node1
                    if constraint_a[i_a] != 0:

                        # 如果是~one变量, 那么创建const node
                        if i_a == 0 and constraint_a[0] != 1:
                            node1 = RNode.new_const_node(constraint_a[0])
                            print("\tCASE4, add a const node as node1, value: %f, id: %d" % (constraint_a[0], node1.id))


                        elif i_a == 0 and constraint_a[0] == 1:
                            node1_flag = True

                        # 如果field为1, 直接取node_list中的node
                        elif constraint_a[i_a] == 1:
                            node1 = RNode.node_list[i_a - 1]
                            print("\tCASE4, choose an existing node as node1, id: %d" % (node1.id,))

                        # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                        else:
                            node1 = RNode.node_list[i_a - 1].mul(RNode.new_const_node(constraint_a[i_a]))
                            print("\tCASE4, mul const node with an existing node as node1, id: %d" % (node1.id,))

                        for i_b in range(var_num):

                            node2 = None
                            node2_flag = False

                            # 创建node2
                            if constraint_b[i_b] != 0:
                                # 如果是~one变量, 那么创建const node
                                if i_b == 0 and constraint_b[0] != 1:
                                    node2 = RNode.new_const_node(constraint_b[0])
                                    print("\t\tCASE4, add a const node as node2, value: %f, id: %d" % (
                                        constraint_b[0], node2.id))
                                elif i_b == 0 and constraint_b[0] == 1:
                                    node2_flag = True

                                # 如果field为1, 直接取node_list中的node
                                elif constraint_b[i_b] == 1:
                                    node2 = RNode.node_list[i_b - 1]
                                    print("\t\tCASE4, choose an existing node as node2, id: %d" % (node2.id,))


                                # field不为1 ,创建const node与node_list中的node相乘,并返回相乘的node
                                else:
                                    node2 = RNode.node_list[i_b - 1].mul(RNode.new_const_node(constraint_b[i_b]))
                                    print(
                                        "\t\tCASE4, mul const node with an existing node as node2, id: %d" % (
                                            node2.id,))

                                if node_left is None:
                                    if node1 is None or (node1.is_const() and node1.const == 1):
                                        if node2_flag:
                                            node2 = RNode.new_const_node(1)
                                        node_left = node2
                                        print(
                                            "\t\tCASE4, node_left is None, choose node2 as node_left, node_left id: %d " % (
                                                node_left.id,))
                                    elif node2 is None or (node2.is_const() and node2.const == 1):
                                        if node1_flag:
                                            node1 = RNode.new_const_node(1)
                                        node_left = node1
                                        print(
                                            "\t\tCASE4, node_left is None, choose node1 as node_left, node_left id: %d" % (
                                                node_left.id))
                                    else:
                                        node_left = node1.mul(node2)
                                        print("\t\tCASE4, node_left is None, id: %d, node1 id: %d. node2 id: %d" % (
                                            node_left.id, node1.id, node2.id))

                                else:
                                    if node1.is_const() and node1.const == 1:
                                        node_left = node_left.add(node2)
                                        print(
                                            "\t\tCASE4, add node2 to node_left, node2 id: %d, node_left id: %d" % (
                                                node2.id, node_left.id,))
                                    elif node2.is_const() and node2.const == 1:
                                        node_left = node_left.add(node1)
                                        print(
                                            "\t\tCASE4, add node1 to node_left, node1 id: %d, node_left id: %d" % (
                                                node1.id, node_left.id))
                                    else:
                                        node_left = node_left.add(node1.mul(node2))
                                        print("\t\tCASE4, add to node_left, id: %d, node1 id: %d. node2 id: %d" % (
                                            node_left.id, node1.id, node2.id))

                # 创建node_right-field1-field2=node3
                node_right = None
                node3_index = -1
                last_index = -1
                node3 = None
                node4 = None
                for i in range(var_num):
                    if constraint_c[i] == 1:
                        node3_index = i
                        print("\tCASE4, find node3, node3 id: %d" % (node3_index - 1,))
                        break

                # 找到c中最后一个不为0的field的下标
                for i in range(var_num):
                    index = var_num - i - 1
                    if index == node3_index:
                        continue
                    elif constraint_c[index] != 0:
                        last_index = index
                        print("\tCASE4, find last node in the add list, node id: %d" % (last_index - 1,))
                        break

                for i in range(var_num):

                    if constraint_c[i] != 0 and i != node3_index and i != last_index:

                        # 构造node4
                        # 如果是~one变量, 那么创建const node
                        if i == 0:
                            node4 = RNode.new_const_node(0 - constraint_c[0])
                        elif constraint_c[i] == -1:
                            node4 = RNode.node_list[i - 1]
                        else:
                            node4 = RNode.node_list[i - 1].mul(RNode.new_const_node(0 - constraint_c[i]))

                        old_node_left_id = node_left.id
                        node_left = node_left.add(node4)
                        print("\tCASE4, add node4 to node_left, new id: %d, old id: %d, node4 id: %d" % (
                            node_left.id, old_node_left_id, node4.id))

                        # if node_right is None:
                        #     node_right = node4
                        #     print("\tCASE4, node_right is None, choose node4, node 4 id: %d" % (node4.id,))
                        #
                        # else:
                        #     old_node_right_id = node_right.id
                        #     node_right = node_right.add(node4)
                        #     print("\tCASE4, add node4 to node_right, new id: %d, old id: %d, node4 id: %d" % (
                        #         node_right.id, old_node_right_id, node4.id))

                    # 利用最后一个node构建node_right
                    elif constraint_c[i] != 0 and i != node3_index and i == last_index:
                        if i == 0:
                            node_right = RNode.new_const_node(0 - constraint_c[0])
                        elif constraint_c[i] == -1:
                            node_right = RNode.node_list[i - 1]
                        else:
                            node_right = RNode.node_list[i - 1].mul(RNode.new_const_node(0 - constraint_c[i]))

                if node3_index == 0:
                    node3 = RNode.new_const_node(1)
                else:
                    node3 = RNode.node_list[node3_index - 1]

                print("\tCASE4, node_left+node_right=node3, left id: %d, right id: %d, node3 id: %d" % (
                    node_left.id, node_right.id, node3.id))

                node3.op = Op.ADD
                node3.add_father(node_right)
                node3.add_father(node_left)
                node_left.add_child(node3)
                node_right.add_child(node3)

        for node in RNode.node_list:
            node.print()

    return RNode.node_list


def node_weight_test():
    # dg = util.graph_generation(RNode.node_list, False)
    # adj_matrix = util.matrix_generation(dg)
    # pr_vec = util.pr_vector_generation(dg)
    # vec = pr.pagerank(adj_matrix, pr_vec, False)

    w_calc = Weight_Calculator(False, False, False)
    w_calc.graph_generation_from_rnode(RNode.node_list)
    vec = w_calc.pgrank_calculation()

    for i, node in enumerate(RNode.node_list):
        node.weight = vec[i]


def cover_algorithm_1_test() -> List[TileNode]:
    res: List[TileNode] = []
    tile_candidate: List[TileNode] = []
    tile_num = 1

    # 选择rnode_list中的无子节点的node作为tile_root的candidate
    root_candidate: List[RNode] = []
    for node in RNode.node_list:
        if len(node.child) == 0:
            root_candidate.append(node)

    while len(root_candidate) != 0:
        print("************************************************")
        print("TILE {0}".format(tile_num))
        tile_num += 1

        s = ""
        for node in root_candidate:
            s = s + "node {0},".format(node.id)
        print("root candidate: " + s)

        print("-------------------------")
        for node in root_candidate:
            t_node: TileNode = TileNode.create_tile_node_from_rnode(node)
            t_node.get_tile()
            tile_candidate.append(t_node)

        # TODO: tile权重的计算与选取, 目前每次正好只有一个candidate
        print("-------------------------")
        tile: TileNode = None
        tile, tile_id = choose_tile(tile_candidate)
        print("choose tile {0}, root is rnode {1}".format(tile_id, tile.id))

        res.append(tile)
        tile.show_tile()
        # 从RNode DAG中删除所选出的瓦片所包含的边
        tile.remove_tile_from_tree()

        # 更新root_candidate, 清空tile_candidate:
        root_candidate.clear()

        for node in RNode.node_list:
            if len(node.child) == 0 and len(node.father) != 0:
                root_candidate.append(node)

        tile_candidate.clear()

    print("************************************************")

    return res


def tile_weight_calc(tiles: List[TileNode]):
    for tile in tiles:
        tile.show_tile()
        print("************************************************")

    # 为瓦片构建新的数据流图, 并使用pagerank算法计算各节点的权重
    # dg = util.graph_generation_from_tile_node(tiles, True)
    # adj_matrix = util.matrix_generation(dg)
    # pr_vec = util.pr_vector_generation(dg)
    # vec = pr.pagerank(adj_matrix, pr_vec, False)

    w_calc = Weight_Calculator(True, True, True)
    w_calc.graph_generation_from_tile_node(tiles)
    vec = w_calc.pgrank_calculation()
    dg = w_calc.dg


    # 设置 rnode中quadratic的weight 和 degree
    for index, node in enumerate(dg.nodes()):
        if dg.nodes[node]["name"].startswith("q"):
            id = int(dg.nodes[node]["name"][1:])
            RNode.node_list[id].weight = vec[index]
            RNode.node_list[id].degree = dg.out_degree[dg.nodes[node]["name"]] + dg.in_degree[dg.nodes[node]["name"]]
            # print("set q%d's degree: %d" % (id, RNode.node_list[id].degree))

    # 更新node的pr值
    for index, node in enumerate(dg.nodes()):
        dg.nodes[node]["pr"] = vec[index]
        # print(dg.nodes[node]["pr"])
        # print(dg.nodes[node]["name"])
        print(dg.nodes[node]["pg_weight"])

    # 为各个瓦片创建节点集合
    node_set = [set() for _ in range(len(tiles))]

    for index, tile in enumerate(tiles):
        node_set[index] = tile.create_node_set()
        print(node_set[index])

    # 计算各瓦片的权重
    tile_weight = [0 for _ in range(len(tiles))]

    linear_index = 0
    for index, tile in enumerate(tiles):
        weight = 0

        # 计算二次瓦片的weight
        if tile.is_quadratic():
            if len(node_set[index]) == 3:
                for i in node_set[index]:
                    weight += dg.nodes["q" + str(i)]["pr"]
                weight /= 3

            else:
                for i in node_set[index]:
                    if i == tile.id:
                        weight += dg.nodes["q" + str(i)]["pr"]
                    else:
                        weight += dg.nodes["q" + str(i)]["pr"] * 2
                weight /= 3

        else:
            weight = dg.nodes["l" + str(linear_index)]["pr"]
            linear_index += 1

        tile_weight[index] = weight

    print(tile_weight)

    return tile_weight


def constraint_generation(tile_list: List[TileNode], tile_weight: List[float]):
    consgen = Consgen(tile_list, tile_weight)
    res = consgen.cons_generation()
    return res
