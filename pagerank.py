import numpy as np
import matplotlib.pyplot as plt


alpha = 0.85  # 跳转因子


def draw(iter_list, pr_list):
    """
    绘制收敛图
    :param iter_list: 迭代次数列表
    :param pr_list: 每一个向量的值
    :return:
    """
    plt.plot(iter_list, pr_list)
    plt.show()


def pagerank(adj_matrix, pr_vec, draw_flag=False):
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
    num_nodes = np.size(adj_matrix, 1)  # 获得矩阵列数(ie. 节点数)
    jump_value = (1 - alpha) / num_nodes  # 从其他页面跳转入所在页面的概率(标量)
    jump_vec = jump_value * np.ones(num_nodes)  # 向量化

    iter_list = []
    pr_list = []

    for n_iter in range(1, 201):
        pr_new = alpha * np.dot(pr_vec, adj_matrix) + jump_vec

        print("第{0}次迭代的PR值:{1}".format(n_iter, pr_new))

        iter_list.append(n_iter)
        pr_list.append(tuple(pr_new))

        # 收敛条件
        if (np.abs(pr_new - pr_vec)<0.00001).all():
            break

        pr_vec = pr_new


    print("迭代完成!")
    print("收敛值为:", pr_vec)

    if draw_flag is True:
        draw(iter_list, pr_list)

    return pr_vec