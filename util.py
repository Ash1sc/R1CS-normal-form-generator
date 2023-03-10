import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from mynodes.tilenode import *

TXT_PATH = "constraints/constraint2.txt"


def make_matrix():
    f = open(TXT_PATH, "r")
    lines = f.readlines()

    row = line = 0
    for index, l in enumerate(lines):
        if index == 1:
            row = len(l.split(","))
        if l.startswith("B"):
            line = index - 1

    matrices = [[[0] * row for _ in range(line)] for _ in range(3)]

    matrix_id = -1
    prev_line_index = 0
    for i, l in enumerate(lines):
        if l.startswith("A") or l.startswith("B") or l.startswith("C"):
            matrix_id += 1
            prev_line_index = i
            continue

        fields = l.split(",")
        for j, num in enumerate(fields):
            matrices[matrix_id][i - prev_line_index - 1][j] = int(num)

    # 确保每一条限制中c的field中一定有一个是1
    # 以每条限制中不为常数项的field中大于0的最小的数为基准放缩
    # 如果所有不为常数项的field均小于0, 那么以最大的数为基准放缩
    for k in range(len(matrices[0])):

        # 找到限制组c中大于等于1的最小的数
        target = 0

        # 整个约束仅常数项的field非0
        if len([i for i in matrices[2][k] if i != 0]) == 1 and matrices[2][k][0] != 0:
            target = matrices[2][k][0]
            continue

        for j in range(len(matrices[0][0])):

            # target=0时必须更新
            # target>0时,只会选择在0到target之间的数
            # target<0时,会选择大于0或者大于target小于0的数
            if target == 0 or (0 < matrices[2][k][j] < target) or (
                    target < 0 and (matrices[2][k][j] > 0 or target < matrices[2][k][j] < 0)):
                # print("c[%d][%d]: %d, target %d" % (k, j, matrices[2][k][j], target))
                target = matrices[2][k][j]

        # 限制组a与c同时放缩至1/target
        for j in range(len(matrices[0][0])):
            matrices[0][k][j] = matrices[0][k][j] / target
            matrices[2][k][j] = matrices[2][k][j] / target

    return matrices[0], matrices[1], matrices[2]


def get_init_pr(dg):
    """
    获得每个节点的初始pr值
    :param dg: 有向图
    :return:
    """

    node_num = dg.number_of_nodes()
    for node in dg.nodes:
        pr = 1 / node_num
        dg.add_nodes_from([node], pr=pr)


def create_network(node_list):
    """
    创建有向图
    :return: 有向图
    """

    dg = nx.DiGraph()
    # dg.add_nodes_from([0,1,2,3,4])
    # dg.add_edges_from([(1,0), (2, 1), (3, 4), (4, 1), (3, 1)])  # 添加边

    for node in node_list:
        dg.add_node(node.id, op=node.op.name)

    for node in node_list:
        for c in node.child:
            dg.add_edge(node.id, c.id)

    get_init_pr(dg)

    return dg


def draw_network(dg):
    """
    可视化有向图
    :param dg: 有向图
    """
    fig, ax = plt.subplots()
    nx.draw(dg, ax=ax, with_labels=True)
    plt.show()


def graph_generation(node_list, draw_flag=False):
    dg = create_network(node_list)

    if draw_flag is True:
        draw_network(dg)
    return dg


def solve_ranking_leaked(adj_matrix):
    """
    解决排名泄露问题
    :param adj_matrix: 邻接矩阵
    """
    col_num = np.size(adj_matrix, 1)  # 获得邻接矩阵列数

    row_num = 0
    for row in adj_matrix:
        # 如果排名泄露，那么这个节点对每个节点都有出链
        if sum(row) == 0:
            for col in range(col_num):
                adj_matrix[row_num][col] = 1
        row_num += 1


def calc_out_degree_ratio(adj_matrix):
    """
    计算每个节点影响力传播的比率，即该节点有多大的概率把影响力传递给下一个节点
    公式：
        out_edge / n
        out_edge: 出边，即这个节点可以把影响力传递给下一个节点
        n: 这个节点共有多少个出度
    :param adj_matrix: 邻接矩阵
    """
    row_num = 0
    for row in adj_matrix:
        n = sum(row)  # 求该节点的所有出度
        col_num = 0
        for col in row:
            adj_matrix[row_num][col_num] = col / n  # out_edge / n
            col_num += 1

        row_num += 1


def matrix_generation(dg):
    """
    通过有向图生成邻接矩阵
    :param dg: 有向图
    :return adj_matrix: 邻接矩阵
    """
    # node_num = dg.number_of_nodes()
    #
    # adj_matrix = np.zeros((node_num, node_num))
    #
    # for edge in dg.edges:
    #     adj_matrix[int(edge[0])][int(edge[1])] = 1
    #
    # solve_ranking_leaked(adj_matrix)
    # calc_out_degree_ratio(adj_matrix)
    # # print(adj_matrix)

    adj_matrix = np.array(nx.adjacency_matrix(dg).todense())
    solve_ranking_leaked(adj_matrix)
    calc_out_degree_ratio(adj_matrix)
    return adj_matrix


def pr_vector_generation(dg):
    """
    创建初始PR值的向量
    :param dg: 有向图
    :return pr_vec: 初始PR值向量
    """
    pr_list = []
    nodes = dg.nodes

    # 将初始PR值存入列表
    for node in nodes:
        pr_list.append(nodes[node]['pr'])

    pr_vec = np.array(pr_list)  # 将列表转换为ndarray对象

    return pr_vec


def create_network_from_tile_node(tile_list: List[TileNode]):
    quadratic: List[TileNode] = []
    linear: List[TileNode] = []

    node_dict={}

    dg = nx.DiGraph()

    for tile in tile_list:
        if tile.is_quadratic():
            quadratic.append(tile)
        else:
            linear.append(tile)

    s_q = [set() for _ in range(len(quadratic))]
    s_l = [set() for _ in range(len(linear))]

    # 对于二次约束, 保留原本node
    for index, tile in enumerate(quadratic):

        dg.add_node("q" + str(tile.id))
        for f in tile.tile_father:
            dg.add_node("q" + str(f.id))
            dg.add_edge("q" + str(f.id), "q" + str(tile.id))

        s_q[index] = tile.create_node_set()

    # 对于线性约束,做一次抽象, 在dg中只保留一个大的node
    for index, tile in enumerate(linear):
        dg.add_node("l" + str(index))
        s_l[index] = tile.create_node_set()

    for s in s_l:
        print(s)
    for s in s_q:
        print(s)

    # 加边
    # 线性与二次之间的边
    for l_index, l_node in enumerate(s_l):
        u = -1
        v = -1
        # 遍历线性约束抽象node中的每一个节点
        for l_id in l_node:

            # 当前node是线性约束的根,所以他是线性与二次之间的边的前驱
            if l_id == linear[l_index].id:
                u = "l" + str(l_index)
                for q_index, q_set in enumerate(s_q):
                    for q_id in q_set:
                        if q_id == l_id:
                            dg.add_edge(u, "q" + str(q_id))
            # 当前node不是线性约束的根,所以他是线性与二次之间的边的后继
            else:
                v = "l" + str(index)
                for q_index, q_set in enumerate(s_q):
                    for q_id in q_set:
                        if q_id == l_id:
                            dg.add_edge("q" + str(q_id), v)

    # 二次和二次之间的边, a*b=c,加入每一个c指向其他节点的ab的边
    for q_index, q_set in enumerate(s_q):
        u = "q" + str(quadratic[q_index].id)

        for q_index_2, q_set_2 in enumerate(s_q):
            if q_index_2 == q_index:
                continue

            if quadratic[q_index].id in q_set_2 and quadratic[q_index_2].id != quadratic[q_index].id:
                print("add edge from q%d to q%d" % (quadratic[q_index].id, quadratic[q_index_2].id))
                dg.add_edge(u, "q" + str(quadratic[q_index_2].id))

    get_init_pr(dg)

    return dg


def graph_generation_from_tile_node(tile_list: List[TileNode], draw_flag=False):
    dg = create_network_from_tile_node(tile_list)

    if draw_flag is True:
        draw_network(dg)
    return dg
