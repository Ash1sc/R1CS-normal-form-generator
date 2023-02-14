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

    return matrices[0], matrices[1], matrices[2]
