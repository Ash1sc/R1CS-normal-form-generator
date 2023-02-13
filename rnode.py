from enum import Enum


class Op(Enum):
    NULL = 0
    ADD = 1
    MUL = 2


class RNode:  # 对于类的定义我们要求首字母大写

    def __init__(self, id, op, name="_", child=[], father=[]):  # 初始化类的属性
        self.id = id
        self.op = op
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

        if len(self.father)>0:
            print("\tFather:")
            for f in self.father:
                print("\t\t%s" % (f.to_string(),))
        if len(self.child) > 0:
            print("\tChild:")
            for c in self.child:
                print("\t\t%s" % (c.to_string(),))

    def add_child(self, c):
        self.child.append(c)

    def add_father(self, f):
        self.father.append(f)

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
