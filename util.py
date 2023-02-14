TXT_PATH = "./constraints.txt"


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


    #   确保每一条限制中c的field中一定有一个是1
    for k in range(len(matrices[0])):

        # 找到限制组c中大于等于1的最小的数
        target = 0

        for j in range(len(matrices[0][0])):
            if target == 0 or (0 < matrices[2][k][j] < target):
                # print("c[%d][%d]: %d, target %d" % (k, j, matrices[2][k][j], target))
                target = matrices[2][k][j]

        # 限制组a与c同时放缩至1/target
        for j in range(len(matrices[0][0])):
            matrices[0][k][j] = matrices[0][k][j] / target
            matrices[2][k][j] = matrices[2][k][j] / target

    return matrices[0], matrices[1], matrices[2]
