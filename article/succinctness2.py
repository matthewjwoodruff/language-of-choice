from math import isinf

def memoize(f):
    def memoized(*args):
        try: return memoized._memos[args]
        except KeyError:
            result = memoized._memos[args] = f(*args)
            return result
    memoized._memos = dict()
    return memoized

class Node(object):
    __invert__ = lambda self: self(const1, const0)
    __and__ = lambda self, other: self(const0, other)
    __or__ = lambda self, other: self(other, const1)
    __xor__ = lambda self, other: self(other, ~other)

def Equiv(p, q): return p(~q, q)
def Implies(p, q): return p(const1, q)

class ConstantNode(Node):
    rank = float('Inf')
    def __init__(self, name, value): self.name, self.value = name, value
    def evaluate(self, env): return self.value
    def __call__(self, *branches): return branches[self.value]
    def __repr__(self): return self.name

Constant = memoize(ConstantNode)
const0, const1 = Constant("0", 0), Constant("1", 1)

def Variable(name, rank): return build_node(name, rank, const0, const1)

class ChoiceNode(Node):
    value = None
    def __init__(self, name, rank, if0, if1):
        assert rank < if0.rank and rank < if1.rank
        self.name = name
        self.rank = rank
        self.if0 = if0
        self.if1 = if1

    def evaluate(self, env):
        branch = (self.if0, self.if1)[env[self.rank]]
        return branch.evaluate(env)

    def __call__(self, if0, if1):
        # special cases from c a & i
        if if0 is if1: return if0
        if (if0, if1) == (const0, const1): return self
        return build_choice(self, if0, if1)

    def __repr__(self):
        if (self.if0, self.if1) == (const0, const1): return self.name
        elif (self.if0, self.if1) == (const1, const0): return "~{}".format(self.name)
        return "{}({}, {})".format(self.name, repr(self.if0), repr(self.if1))

build_node = memoize(ChoiceNode)

@memoize
def build_choice(node, if0, if1):
    # assumes node, if0, and if1 are standardized, and
    # builds a standardized graph
    top = float("Inf")
    tname = node.name
    for n in (node, if0, if1):
        if n.rank < top:
            top = n.rank
            tname = n.name

    cases = [subst(node, top, value)(subst(if0, top, value),
                                     subst(if1, top, value))
             for value in (0, 1)]
    new_node = make_node(tname, top, *cases)
    print("{}({}, {}) = {}".format(node, if0, if1, new_node))
    return new_node

def make_node(name, rank, if0, if1):
    if if0 is if1: return if0
    return build_node(name, rank, if0, if1)

def subst(node, rank, value):
    # this function does the c a & i / swapping
    if rank < node.rank: return node
    elif rank == node.rank: return (node.if0, node.if1)[value]
    else:                   return make_node(node.name, node.rank,
                                             subst(node.if0, rank, value),
                                             subst(node.if1, rank, value))

a = Variable('a', 0)
b = Variable('b', 1)
c = Variable('c', 2)
p = Variable('p', 3)
q = Variable('q', 4)

print("Building p(a, q(b,c))")
p(a, q(b,c))
print("Building q(p(a,b), p(a,c))")
q(p(a,b), p(a,c))
print("Building ~q(p(a,b), p(a,c))")
~q(p(a,b), p(a,c))
print("Building Equiv(p(a, q(b,c)), q(p(a,b), p(a,c)))")
Equiv(p(a, q(b,c)), q(p(a,b), p(a,c)))
