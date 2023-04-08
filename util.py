import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from mynodes.tilenode import *


# TXT_PATH = "constraints/constraints.txt"


def make_matrix(path):
    f = open(path, "r")
    lines = f.readlines()

    row = line = 0
    for index, l in enumerate(lines):
        if index == 1:
            row = len(l.split(","))
        if l.startswith("B"):
            line = index - 1

    matrices = [[[0.0] * row for _ in range(line)] for _ in range(3)]

    matrix_id = -1
    prev_line_index = 0
    for i, l in enumerate(lines):
        if l.startswith("A") or l.startswith("B") or l.startswith("C"):
            matrix_id += 1
            prev_line_index = i
            continue

        fields = l.split(",")
        for j, num in enumerate(fields):
            matrices[matrix_id][i - prev_line_index - 1][j] = float(num)

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


def make_txt(a: np.ndarray, b: np.ndarray, c: np.ndarray, path: str):
    f = open(path, 'w')

    lines: List[str] = ["A\n"]

    for i in range(a.shape[0]):
        line = ""
        for j in range(a.shape[1] - 1):
            line = line + "{0},".format(a[i][j])
        line = line + str(a[i][a.shape[1] - 1])+"\n"
        lines.append(line)
    lines.append("B\n")
    for i in range(b.shape[0]):
        line = ""
        for j in range(b.shape[1] - 1):
            line = line + "{0},".format(b[i][j])
        line = line + str(b[i][b.shape[1] - 1])+"\n"
        lines.append(line)
    lines.append("C\n")
    for i in range(c.shape[0]):
        line = ""
        for j in range(c.shape[1] - 1):
            line = line + "{0},".format(c[i][j])
        line = line + str(c[i][c.shape[1] - 1])+"\n"
        lines.append(line)
    f.writelines(lines)
