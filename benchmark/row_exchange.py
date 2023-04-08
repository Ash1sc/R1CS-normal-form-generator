from consgen import *
from util import *
import numpy as np


def exchange_row(i, j, a, b, c):
    m_a = np.array(a)
    m_b = np.array(b)
    m_c = np.array(c)

    new_a = m_a.copy()
    new_b = m_b.copy()
    new_c = m_c.copy()

    n = new_a.shape[0]

    for index in range(n):
        tmp = new_a[index][i]
        new_a[index][i] = new_a[index][j]
        new_a[index][j] = tmp

        tmp = new_b[index][i]
        new_b[index][i] = new_b[index][j]
        new_b[index][j] = tmp

        tmp = new_c[index][i]
        new_c[index][i] = new_c[index][j]
        new_c[index][j] = tmp

    return new_a, new_b, new_c


def main():
    a, b, c = make_matrix("../constraints/constraints.txt")

    new_a, new_b, new_c = exchange_row(0, 0, a, b, c)
    make_txt(new_a, new_b, new_c, "row_exchange/row_exchange_{0}_{1}.txt".format(0, 0))

    for i in range(1, len(a[0])):
        for j in range(i + 1, len(a[0])):
            new_a, new_b, new_c = exchange_row(i, j, a, b, c)
            make_txt(new_a, new_b, new_c, "row_exchange/row_exchange_{0}_{1}.txt".format(i, j))


if __name__ == '__main__':
    main()
