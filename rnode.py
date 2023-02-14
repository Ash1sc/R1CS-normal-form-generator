from enum import Enum


class Op(Enum):
    NULL = 0
    ADD = 1
    MUL = 2


class RNode:  # 对于类的定义我们要求首字母大写

    CONST_NAME = "~one"
    node_list = []
    current_id = 0

    @classmethod
    def new_node(cls, op=Op.NULL, name="_", con=0):
        node = RNode(RNode.current_id, op, name, con)
        RNode.node_list.append(node)
        RNode.current_id += 1

        return node

    @classmethod
    def clear(cls):
        RNode.current_id = 0
        RNode.node_list = []
        print("Clear the node list")

    def __init__(self, id, op=Op.NULL, name="_", con=0, child=[], father=[]):  # 初始化类的属性
        self.id = id
        self.op = op
        self.const = con
        self.name = name
        self.child = []
        for c in child:
            self.child.append(c)

        self.father = []
        for f in father:
            self.father.append(f)

    def to_string(self):
        return "Node id: %d, name: %s, op: %s" % (self.id, self.name, self.op.name)

    def print(self):
        print(self.to_string())

        if len(self.father) > 0:
            print("\tFather:")
            for f in self.father:
                print("\t\t%s" % (f.to_string(),))
        if len(self.child) > 0:
            print("\tChild:")
            for c in self.child:
                print("\t\t%s" % (c.to_string(),))

    def add_child(self, c):
        self.child.append(c)
        c.father.append(self)

    def add_father(self, f):
        self.father.append(f)
        f.child.append(self)

    def remove_child(self, c):
        for node in self.child:
            if node.id == c.id:
                self.child.remove(node)
                break

    def remove_father(self, f):
        for node in self.father:
            if node.id == f.id:
                self.father.remove(node)
                break

    def have_mul(self, node):
        """
        判断与node是否已有乘号直接连接
        :param node:
        :return: 与node相连接的乘号node
        """
        for c in self.child:
            if c.op == Op.MUL:
                for f in c.father:
                    if f.id == node.id:
                        return c

        return None

    def have_add(self, node):
        """
        判断与node是否已有加号直接连接
        :param node:
        :return: 与node相连接的加号node
        """
        for c in self.child:
            if c.op == Op.ADD:
                for f in c.father:
                    if f.id == node.id:
                        return c

        return None

    def add(self, node):
        """
        与另一个node相加
        :param node:
        :return: 相加后中间变量的node
        """
        result = RNode.new_node(Op.ADD)
        self.child.append(result)
        node.child.append(result)
        result.father.append(self)
        result.father.append(node)

        return result

    def mul(self, node):
        """
        与另一个node相乘
        :param node:
        :return: 相乘后中间变量的node
        """
        result = RNode.new_node(Op.MUL)
        self.child.append(result)
        node.child.append(result)
        result.father.append(self)
        result.father.append(node)

        return result
