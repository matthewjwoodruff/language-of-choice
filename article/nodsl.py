"""
nodsl.py

Attempt to express the language of choice without
overloading operators.

I understand why the article did it, and I'm impressed
that it works so well, but it's hard to follow what's
happening.  Too much magic for me.

I think partly it's because the article conflates variables
and choices.  A variable's role is to participate in
choices, either as an index or as a branch, but not to
*be* a choice.
"""

class Node(object):
    pass

class ConstantNode(Node):
    def __init__(self, name, value):
        self.rank = float("Inf")
        self.value = value
        self.name = name
    def __repr__(self): return self.name
    def evaluate(self, _): return self.value

class Variable(object):
    """
    A variable is not a node in the BDD!
    """
    def __init__(self, name, rank):
        self.name = name
        self.rank = rank
    def __repr__(self): return self.name
    def evaluate(self, env): return env[self.rank]

class ChoiceNode(Node):
    def __init__(self, index, if0, if1):
        """
        index is a constant, variable, or another choice node
        """
        self.index = index
        self.if0 = if0
        self.if1 = if1
        self.rank = self.index.rank
    def __repr__(self):
        return "{}({},{})".format(repr(self.index), repr(self.if0), repr(self.if1))
    def evaluate(self, env):
        fork = self.index.evaluate(env)
        if fork == 0:
            return self.if0.evaluate(env)
        elif fork == 1:
            return self.if1.evaluate(env)
        raise Exception()

def subst(index, rank, value):
    if index == constants[0]:
        return index
    if index == constants[1]:
        return constants[1]
    if rank < index.rank: return index
    try:
        if0 = index.if0
        if1 = index.if1
    except AttributeError:
        if0 = constants[0]
        if1 = constants[1]
    if rank == index.rank:
        if value == 0:
            return if0
        if value == 1:
            return if1
        raise Exception()
    _if0 = subst(if0, rank, value)
    _if1 = subst(if1, rank, value)
    if _if0 is _if1: return _if0
    return choice(index, _if0, _if1)

# one global dictionary for choices
# Keys: (index, if0, if1)
choices = dict()

def choice(index, if0, if1):
    global choices
    try:
        return choices[(index, if0, if1)]
    except KeyError: pass
    choices[(index, if0, if1)] = ChoiceNode(index, if0, if1)
    print("choice {} {} {}".format(index, if0, if1))
    if index == constants[0]:
        return if0
    if index == constants[1]:
        return if1
    if if0 == constants[0] and if1 == constants[1]:
        return choices[(index, if0, if1)]

    top = index.rank
    _index = index
    if if0.rank < top:
        top = if0.rank
        _index = if0
    if if1.rank < top:
        top = if1.rank
        _index = if1
    top = min(index.rank, if0.rank, if1.rank)
    _if0 = choice(
        subst(index, top, 0), subst(if0, top, 0), subst(if1, top, 0))
    _if1 = choice(
        subst(index, top, 1), subst(if0, top, 1), subst(if1, top, 1))
    new_node = choice(_index, _if0, _if1)
    return new_node

# one global dictionary for constants
# Key: constant value
constants = dict()
def constant(name, value):
    global constants
    try: return constants[value]
    except KeyError:
        constants[value] = ConstantNode(name, value)
        return constants[value]

variables = dict()
def variable(name, rank):
    global variables
    try:
        variable = variables[rank]
    except KeyError:
        return Variable(name, rank)
    if variable.name != name:
        raise Exception()
    return variable

const0 = constant("0", 0)
const1 = constant("1", 1)
a = variable('a', 0)
b = variable('b', 1)
c = variable('c', 2)
p = variable('p', 3)
q = variable('q', 4)

left = choice(p, a, choice(q, b, c))
right = choice(q, choice(p, a, b), choice(p, a, c))

print("left {}".format(repr(left)))
print("right {}".format(repr(right)))
