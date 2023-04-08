from consgen import *
from util import *
import numpy as np


def exchange_line(i, j, a, b, c):
    m_a = np.array(a)
    m_b = np.array(b)
    m_c = np.array(c)

    new_a = m_a.copy()
    new_b = m_b.copy()
    new_c = m_c.copy()

    tmpi = new_a[i].copy()
    tmpj = new_a[j].copy()
    new_a[i] = tmpj
    new_a[j] = tmpi

    tmpi = new_b[i].copy()
    tmpj = new_b[j].copy()
    new_b[i] = tmpj
    new_b[j] = tmpi

    tmpi = new_c[i].copy()
    tmpj = new_c[j].copy()
    new_c[i] = tmpj
    new_c[j] = tmpi

    return new_a, new_b, new_c


def main():
    a, b, c = make_matrix("../constraints/constraints.txt")

    new_a, new_b, new_c = exchange_line(0, 0, a, b, c)
    make_txt(new_a, new_b, new_c, "line_exchange/line_exchange_{0}_{1}.txt".format(0, 0))

    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            new_a, new_b, new_c = exchange_line(i, j, a, b, c)
            make_txt(new_a, new_b, new_c, "line_exchange/line_exchange_{0}_{1}.txt".format(i, j))


if __name__ == '__main__':
    main()
