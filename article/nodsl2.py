# This time we'll start with the data structures and the
# methods we expect to need, and then flesh them out.
#
# Instead of saying p(a,b), we'll say choice(p,a,b)
#
# A variable is a ChoiceNode where if0 is const0 and if1
# is const1.  You can't construct a variable using choice()
# because choice requires ChoiceNodes as all three arguments.

from collections import namedtuple
import math
inf = math.inf

def algebra(node):
    try:                   node.if0
    except AttributeError: return node.name
    #try:
    #    if node.if0.value == 0 and node.if1.value == 1:
    #        return node.name
    #    elif node.if1.value == 0 and node.if0.value == 1:
    #        return "~{}".format(node.name)
    #except AttributeError: pass
    return "{}({},{})".format(node.name, algebra(node.if0), algebra(node.if1))

DIG = 10**5

def ids(node):
    try: node.if0
    except AttributeError: return "{}@{}".format(node.name, id(node)%DIG)
    return "{}@{}({},{})".format(node.name, id(node)%DIG, ids(node.if0), ids(node.if1))

# constant nodes are terminal -- they do not have if0 or if1
ConstantNode = namedtuple("ConstantNode", (
    'name',
    'rank',
    'value'))
ConstantNode.__repr__ = algebra

# choice nodes do not have a value in the absolute sense,
# only in the context of an environment
ChoiceNode = namedtuple("ChoiceNode", (
    'name',
    'rank',
    'if0',
    'if1' ))
ChoiceNode.__repr__ = algebra

const0 = ConstantNode('0', inf, 0)
const1 = ConstantNode('1', inf, 1)

choice_nodes = dict()

def variable(name, rank):
    key = (name, rank, const0, const1)
    try:
        return choice_nodes[key]
    except KeyError:
        node = ChoiceNode(*key)
        choice_nodes[key] = node
        return node

def collapse_irrelevant(index, if0, if1):
    if if0 is if1: return if0
    key = (index.name, index.rank, if0, if1)
    try: return choice_nodes[key]
    except KeyError:
        node = ChoiceNode(*key)
        choice_nodes[key] = node
        return node

def substitute(node, rank, value):
    if rank < node.rank: return node
    elif rank == node.rank:
        if value == 0:
            return node.if0
        else:
            return node.if1
    else:
        left = substitute(node.if0, rank, value)
        right = substitute(node.if1, rank, value)
        key = (node.name, node.rank, left, right)
        try: return choice_nodes[key]
        except KeyError:
            node = ChoiceNode(key)
            choice_nodes[key] = node
            return node

def choice(index, if0, if1):
    try:
        if if0.value == 0:
            if if1.value == 0:
                return const0
            elif if1.value == 1:
                return index
        elif if0.value == 1 and if1.value == 1:
            return const1
    except AttributeError: pass
    try:
        if index.value == 0: return if0
        if index.value == 1: return if1
    except AttributeError: pass
    minimum_rank_node = index
    for node in (if0, if1):
        if node.rank < minimum_rank_node.rank:
            minimum_rank_node = node
    rank = minimum_rank_node.rank
    left  = choice(substitute(index, rank, 0),
                   substitute(if0,   rank, 0),
                   substitute(if1,   rank, 0))
    right = choice(substitute(index, rank, 1),
                   substitute(if0,   rank, 1),
                   substitute(if1,   rank, 1))

    new_index = variable(minimum_rank_node.name, minimum_rank_node.rank)
    new_node = collapse_irrelevant(new_index, left, right)

    return new_node

a = variable('a', 0)
b = variable('b', 1)
c = variable('c', 2)
p = variable('p', 3)

import sys
cab = choice(p,a,b)
print(algebra(cab))
print(ids(cab))

q = variable('q', 4)

dist_left = choice(p, a, choice(q, b, c))
dist_right = choice(q, choice(p, a, b), choice(p, a, c))

print(algebra(dist_left))
print(ids(dist_left))
print(algebra(dist_right))
print(ids(dist_right))

print(ids(dist_left) == ids(dist_right))

def viz(graph):
    nodes = [dist_left]
    dot = graphviz.Digraph('distributive')
    while len(nodes) > 0:
        next_nodes = set()
        for node in nodes:
            dot.node(str(id(node)), node.name)
            try:
                next_nodes.add(node.if0)
                dot.edge(str(id(node)), str(id(node.if0)), label='0')
                next_nodes.add(node.if1)
                dot.edge(str(id(node)), str(id(node.if1)), label='1')
            except AttributeError: pass
        nodes = next_nodes

    dot.render('distributive', view=False)

try:
    import graphviz
    viz(dist_left)
except ImportError:
    pass

# scheduling-like constraints
# exactly one of a,b,c,d,e
# exactly one of a,f,g,h,i

choice_nodes.clear()
a = variable('a', 0)
b = variable('b', 1)
c = variable('c', 2)
d = variable('d', 3)
e = variable('e', 4)
f = variable('f', 5)
g = variable('g', 6)
h = variable('h', 7)
i = variable('i', 8)

# exactly one of a,b,c,d,e
abcde = choice(a,
               choice(b,
                      choice(c,
                             choice(d,
                                    e,
                                    choice(e,const1,const0)),
                             choice(d,
                                    choice(e,const1,const0),
                                    const0)
                      ),
                      choice(c,
                             choice(d,
                                    choice(e,const1,const0),
                                    const0),
                             const0
                      )
               ),
               choice(b,
                      choice(c,
                             choice(d,
                                    choice(e,const1,const0),
                                    const0),
                             const0),
                      const0)
               )
# exactly one of a,f,g,h,i
afghi = choice(a,
               choice(f,
                      choice(g,
                             choice(h,
                                    i,
                                    choice(i,const1,const0)),
                             choice(h,
                                    choice(i,const1,const0),
                                    const0)
                      ),
                      choice(g,
                             choice(h,
                                    choice(i,const1,const0),
                                    const0),
                             const0
                      )
               ),
               choice(f,
                      choice(g,
                             choice(h,
                                    choice(i,const1,const0),
                                    const0),
                             const0),
                      const0)
               )
# the two together

abcdefghi = choice(abcde, const0, afghi)

def viz2(graph):
    nodes = [abcdefghi]
    dot = graphviz.Digraph('abcdefghi')
    while len(nodes) > 0:
        next_nodes = set()
        for node in nodes:
            dot.node(str(id(node)), node.name)
            try:
                next_nodes.add(node.if0)
                dot.edge(str(id(node)), str(id(node.if0)), label='0')
                next_nodes.add(node.if1)
                dot.edge(str(id(node)), str(id(node.if1)), label='1')
            except AttributeError: pass
        nodes = next_nodes

    dot.render('abcdefghi', view=False)
try:
    import graphviz
    viz2(abcdefghi)
    print("abcdefghi")
except ImportError:
    pass

# A Possibly More Realistic Example?
# Let's say we want to do a round-robin tournament among
# N teams across M days.  Each team may play at most once
# in a day.
choice_nodes.clear()

