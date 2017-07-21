names = dict()
indentation = 0
def memoize(f):
    def memoized(*args):
        try: return memoized._memos[args]
        except KeyError:
            result = memoized._memos[args] = f(*args)
            return result
    memoized._memos = {}
    return memoized

class Node(object):
    """
    are these lambdas somehow structural, or is this just
    for compactness?
    """
    __invert__ = lambda self: self(const1, const0)
    __and__ = lambda self, other: self(const0, other)
    __or__ = lambda self, other: self(other, const1)
    __xor__ = lambda self, other: self(other, ~other)

def Equiv(p, q): return p(~q, q)
def Implies(p, q): return p(const1, q)

class ConstantNode(Node):
    rank = float("Inf")
    def __init__(self, value): self.value = value
    def evaluate(self, env): return self.value
    def __call__(self, *branches): return branches[self.value]
    def __repr__(self): return repr(self.value)

Constant = memoize(ConstantNode)
const0, const1 = Constant(0), Constant(1)

def Variable(rank):
    return build_node(rank, const0, const1)

class ChoiceNode(Node):
    """ We no longer get a name """
    value = None
    def __init__(self, rank, if0, if1):
        # structural correctness
        assert(rank < if0.rank and rank < if1.rank)
        spaces = "".join([" "]*indentation)

        self.rank = rank
        self.if0 = if0
        self.if1 = if1
    def evaluate(self, env):
        branch = (self.if0, self.if1)[env[self.rank]]
        return branch.evaluate(env)
    def __call__(self, if0, if1):
        if if0 is if1: return if0
        if (if0, if1) == (const0, const1):
            return self
        return build_choice(self, if0, if1)
    def __repr__(self):
        global names
        return "{}({}, {})".format(names[id(self)], names[id(self.if0)], names[id(self.if1)])

build_node = memoize(ChoiceNode)

@memoize
def build_choice(node, if0, if1):
    global indentation
    global names
    indentation += 2
    spaces = "".join([" "] * indentation)
    print("{}building {}({},{})".format(spaces, names[id(node)], names[id(if0)], names[id(if1)]))
    top = min(node.rank, if0.rank, if1.rank)
    print("{}top={}".format(spaces,top))
    cases = [subst(node, top, value)(subst(if0, top, value),
                                     subst(if1, top, value))
             for value in (0,1)]
    #
    print("{}calling make_node for rank {}: ({},{})".format(spaces, top, names[id(if0)], names[id(if1)]))
    newnode = make_node(top, *cases)
    try:
        print("{}got existing node {}".format(spaces,names[id(newnode)]))
    except KeyError:
        names[id(newnode)] = str(id(newnode))[-2:]#"{}({},{})".format(names[id(node)], names[id(cases[0])], names[id(cases[1])])
        print("{}got new node {}".format(spaces,names[id(newnode)]))

    indentation -= 2
    if indentation == 0:
        print("")
    return newnode

def make_node(rank, if0, if1):
    if if0 is if1: return if0
    return build_node(rank, if0, if1)

def subst(node, rank, value):
    if rank < node.rank: return node
    elif rank == node.rank: return (node.if0, node.if1)[value]
    else:                   return make_node(node.rank,
                                             subst(node.if0, rank, value),
                                             subst(node.if1, rank, value))

def is_valid(claim):
    return satisfy(claim, 0) is None

def satisfy(node, goal):
    env = dict()
    while isinstance(node, ChoiceNode):
        """
        This is far too cute.  It's hard to reason about.  Let's unpack it.
        First, we evaluate the RHS.
        Then, we assign the first element of the tuple.
        Then, we assign the second element of the tuple, the value of which
        depends on the first element.

        I've at least parenthesized the assignment to make
        the order of operations a little more explicit.

        Also, the if statements are a little confusing.
        if value is None, that means if0 is a choice.
        Descend into that branch and take _its_ left
        hand branch???  I think this may be a bug, in fact.

        """
        print("{} vs {}".format(node, goal))
        if node.if0.value in (None, goal): (node, env[node.rank]) = (node.if0, 0)
        elif node.if1.value in (None, goal): (node, env[node.rank]) = (node.if1, 1)
        else: return None
    return env if node.value == goal else None

names[id(const0)] = '0'
names[id(const1)] = '1'
a = Variable(0)
names[id(a)] = "a"
b = Variable(1)
names[id(b)] = "b"
c = Variable(2)
names[id(c)] = "c"
p = Variable(3)
names[id(p)] = "p"
q = Variable(4)
names[id(q)] = "q"

print("a: {}".format(repr(a)))
print("b: {}".format(repr(b)))
print("c: {}".format(repr(c)))
print("p: {}".format(repr(p)))
print("q: {}".format(repr(q)))

print("--- q(b,c) ---")
print(repr(q(b,c)))

print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(0,0,0)))))
print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(0,0,1)))))
print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(0,1,0)))))
print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(0,1,1)))))
print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(1,0,0)))))
print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(1,0,1)))))
print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(1,1,0)))))
print(q(b,c).evaluate(dict(zip((q.rank,b.rank,c.rank),(1,1,1)))))

print("\n--- FIRST --- ")
first = p(a, q(b,c))
print("--- SECOND --- ")
second = q(p(a,b), p(a,c))
print("--- CLAIM --- ")
claim = Equiv(first, second)
print("---       ----")

print("q(b,c): {}".format(q(b,c)))
print("p(a, q(b,c)): {}".format(p(a, q(b, c))))

print("Claim {} (Equiv({}, {})".format(claim, first, second))
print("Proof exercise: {}".format(is_valid(claim)))
print(satisfy(first, 1))
