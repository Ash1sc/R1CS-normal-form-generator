import networkx as nx
import numpy as np

from mynodes.tilenode import *
from mynodes.rnode import *

import matplotlib.pyplot as plt


class Weight_Calculator:

    def __init__(self, show_graph, show_info, weighted):
        self.show_graph = show_graph
        self.show_info = show_info
        self.weighted = weighted

        self.alpha = 0.85  # 跳转因子

        self.dg = None
        self.adj_matrix = []
        self.pr_vec = []
        self.vec = []

    def __get_init_pr(self):
        """
        获得每个节点的初始pr值
        :param dg: 有向图
        :return:
        """

        node_num = self.dg.number_of_nodes()
        for node in self.dg.nodes:
            pr = 1 / node_num
            self.dg.add_nodes_from([node], pr=pr)

    def __create_network(self, node_list):
        """
        创建有向图
        :return: 有向图
        """

        self.dg = nx.DiGraph()
        # dg.add_nodes_from([0,1,2,3,4])
        # dg.add_edges_from([(1,0), (2, 1), (3, 4), (4, 1), (3, 1)])  # 添加边

        for node in node_list:
            self.dg.add_node(node.id, op=node.op.name)

        for node in node_list:
            for c in node.child:
                self.dg.add_edge(node.id, c.id)

        self.__get_init_pr()

    def __matrix_generation(self):
        """
        通过有向图生成邻接矩阵
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

        # int matrix to float matrix
        matrix = np.array(nx.adjacency_matrix(self.dg).todense())
        self.adj_matrix = [[float(0)] * len(matrix[0]) for _ in range(len(matrix))]
        for i in range(len(self.adj_matrix)):
            for j in range(len(self.adj_matrix[0])):
                self.adj_matrix[i][j] = float(matrix[i][j])
        # TODO: 调整matrix, 为linear发出的边建立不同的权重
        # adj_matrix[i][j] 表示 i 到 j 有变
        if self.weighted is True:
            print("Set Weight")
        # self.__solve_ranking_leaked()
        # self.__calc_out_degree_ratio()

    def __solve_ranking_leaked(self):
        """
        解决排名泄露问题
        :param adj_matrix: 邻接矩阵
        """
        col_num = np.size(self.adj_matrix, 1)  # 获得邻接矩阵列数

        row_num = 0
        for row in self.adj_matrix:
            # 如果排名泄露，那么这个节点对每个节点都有出链
            if sum(row) == 0:
                for col in range(col_num):
                    self.adj_matrix[row_num][col] = 1
            row_num += 1

    def __calc_out_degree_ratio(self):
        """
        计算每个节点影响力传播的比率，即该节点有多大的概率把影响力传递给下一个节点
        公式：
            out_edge / n
            out_edge: 出边，即这个节点可以把影响力传递给下一个节点
            n: 这个节点共有多少个出度
        :param adj_matrix: 邻接矩阵
        """
        row_num = 0
        for row in self.adj_matrix:
            n = sum(row)  # 求该节点的所有出度
            col_num = 0
            for col in row:
                self.adj_matrix[row_num][col_num] = col / n  # out_edge / n
                col_num += 1

            row_num += 1

    def __pr_vector_generation(self):
        """
        创建初始PR值的向量
        :param dg: 有向图
        :return pr_vec: 初始PR值向量
        """
        pr_list = []
        nodes = self.dg.nodes

        # 将初始PR值存入列表
        for node in nodes:
            pr_list.append(nodes[node]['pr'])

        self.pr_vec = np.array(pr_list)  # 将列表转换为ndarray对象

    def __pagerank(self):
        """
        pagerank算法:
            V_{i+1} = alpha * V_i * adj + ((1 - alpha) / N) * E
        收敛条件:
            1. V_{i+1} == V_i
            2. 迭代次数200次
        就是说如果PR向量并没有发生改变，那么收敛结束，得到的PR值就是最终的PR值
        但是假设迭代次数过高后且未发生收敛，那么就会陷入死循环等，根据前人总结的经验，设置为迭代200次
        :param draw_flag: 是否绘图
        :param adj_matrix: 邻接矩阵
        :param pr_vec: 每个节点PR值的初始向量
        :return:
        """
        num_nodes = np.size(self.adj_matrix, 1)  # 获得矩阵列数(ie. 节点数)
        jump_value = (1 - self.alpha) / num_nodes  # 从其他页面跳转入所在页面的概率(标量)
        jump_vec = jump_value * np.ones(num_nodes)  # 向量化

        iter_list = []
        pr_list = []

        for n_iter in range(1, 201):
            pr_new = self.alpha * np.dot(self.pr_vec, self.adj_matrix) + jump_vec

            print("第{0}次迭代的PR值:{1}".format(n_iter, pr_new))

            iter_list.append(n_iter)
            pr_list.append(tuple(pr_new))

            # 收敛条件
            if (np.abs(pr_new - self.pr_vec) < 0.00001).all():
                break

            self.pr_vec = pr_new

        print("迭代完成!")
        print("收敛值为:", self.pr_vec)

        if self.show_info is True:
            draw(iter_list, pr_list)

        self.vec = self.pr_vec

    def __create_network_from_tile_node(self, tile_list: List[TileNode]):
        quadratic: List[TileNode] = []
        linear: List[TileNode] = []

        self.dg = nx.DiGraph()

        for tile in tile_list:
            if tile.is_quadratic():
                quadratic.append(tile)
            else:
                linear.append(tile)

        s_q = [set() for _ in range(len(quadratic))]
        s_l = [set() for _ in range(len(linear))]

        # 对于二次约束, 保留原本node
        for index, tile in enumerate(quadratic):

            self.dg.add_node("q" + str(tile.id), name="q" + str(tile.id))

            for f in tile.tile_father:
                self.dg.add_node("q" + str(f.id), name="q" + str(f.id))
                self.dg.add_edge("q" + str(f.id), "q" + str(tile.id))

            s_q[index] = tile.create_node_set()

        # 对于线性约束,做一次抽象, 在dg中只保留一个大的node
        for index, tile in enumerate(linear):
            self.dg.add_node("l" + str(index), name="l" + str(index))
            s_l[index] = tile.create_node_set()

        # for s in s_l:
        #     print(s)
        # for s in s_q:
        #     print(s)

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
                                self.dg.add_edge(u, "q" + str(q_id))
                # 当前node不是线性约束的根,所以他是线性与二次之间的边的后继
                else:
                    v = "l" + str(l_index)
                    for q_index, q_set in enumerate(s_q):
                        # print("l%d, q%d:" % (l_index, q_index))
                        for q_id in q_set:
                            # print("\tq_id: %d,l_id: %d" % (q_id, l_id))
                            if q_id == l_id:
                                self.dg.add_edge("q" + str(q_id), v)

        # 二次和二次之间的边, a*b=c,加入每一个c指向其他节点的ab的边
        for q_index, q_set in enumerate(s_q):
            u = "q" + str(quadratic[q_index].id)

            for q_index_2, q_set_2 in enumerate(s_q):
                if q_index_2 == q_index:
                    continue

                if quadratic[q_index].id in q_set_2 and quadratic[q_index_2].id != quadratic[q_index].id:
                    # print("add edge from q%d to q%d" % (quadratic[q_index].id, quadratic[q_index_2].id))
                    self.dg.add_edge(u, "q" + str(quadratic[q_index_2].id))

        # 线性与线性之间的边:
        for l_index1, l_node1 in enumerate(s_l):
            for l_index2, l_node2 in enumerate(s_l):

                if l_index1 == l_index2:
                    continue

                flag = False
                for l_id1 in l_node1:
                    if l_id1 in l_node2:
                        flag = True
                        break

                if flag:
                    self.dg.add_edge("l" + str(l_index1), "l" + str(l_index2))

        self.__get_init_pr()

    def pgrank_calculation(self):
        self.__matrix_generation()
        self.__pr_vector_generation()
        self.__pagerank()

        return self.vec

    def graph_generation_from_rnode(self, node_list):
        self.__create_network(node_list)
        if self.show_graph is True:
            fig, ax = plt.subplots()
            nx.draw(self.dg, ax=ax, with_labels=True)
            plt.show()

    def graph_generation_from_tile_node(self, tile_list: List[TileNode]):
        self.__create_network_from_tile_node(tile_list)
        if self.show_graph is True:
            fig, ax = plt.subplots()
            nx.draw(self.dg, ax=ax, with_labels=True)
            plt.show()


def draw(iter_list, pr_list):
    """
    绘制收敛图
    :param iter_list: 迭代次数列表
    :param pr_list: 每一个向量的值
    :return:
    """
    plt.plot(iter_list, pr_list)
    plt.show()
