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

import random

def viz2(graph):
    nodes = [abcdefghi]
    dot = graphviz.Digraph('abcdefghi')
    while len(nodes) > 0:
        next_nodes = set()
        for node in nodes:
            dot.node(str(id(node)), node.name)
            try:
                if node.if0 is const0:
                    zero = str(random.random())
                    dot.node(zero, "0")
                    dot.edge(str(id(node)), zero, label='0')
                elif node.if0 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='0')
                else:
                    dot.edge(str(id(node)), str(id(node.if0)), label='0')
                    next_nodes.add(node.if0)

                if node.if1 is const0:
                    zero = str(random.random())
                    dot.node(zero, "0")
                    dot.edge(str(id(node)), zero, label='1')
                elif node.if1 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='1')
                else:
                    dot.edge(str(id(node)), str(id(node.if1)), label='1')
                    next_nodes.add(node.if1)
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

N = 4
M = 4

variables = list()
rank = 0
for ww in range(M):
    for ii in range(N):
        for jj in range(ii+1,N):
            name = "{}{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj), ww)
            variables.append(variable(name, rank))
            rank += 1
        name = "{}B{}".format(chr(ord('a')+ii), ww)
        variables.append(variable(name, rank))
        rank += 1

print([(v.name, v.rank) for v in variables])

constraints = list()

def at_least_one(vars):
    # early return for trivial failure
    if len(vars) == 0: return const0

    # if only one variable, success on right branch, failure on the left
    constraint = vars.pop()
    while len(vars) > 0:
        constraint = choice(vars.pop(), constraint, const1)

    return constraint

'''
def at_least_two(vars):
    if len(vars) == 0: return const0
    count = 0
    index = 0
    stack = list() # left, right
    leaf = const1
    while True:
        if index < 0: break
        variable = vars[index]
        if index >= len(stack):
            stack.append(tuple())
            if index + 1 == len(vars):
                # terminal
                if count == 0:
                    stack[index] = (const0, const0)
                elif count == 1:
                    stack[index] = (const0, const1)
                else:
                    stack[index] = (const1, const1)
            else:
                stack[index] =

        else:
            if len(stack[index]) == 2:
                left, right = *stack.pop()
                leaf = choice(vars[index], left, right)
            elif len(stack[index]) == 1:
                left, = *stack.pop()
                stack.append((left, leaf))
            elif len(stack[index]) == 0:
                stack[index] = (leaf,)
                index += 1
'''

#
#
#
#





#def exactly_one(vars):
#    stack = list() # (variable, left, right)
#    state = 0
#    index = 0
#    current = [vars[index], None, None]
#    stack.append(current)
#    index += 1
#    while index > 0:
#        if current[1] is None:
#            if index == len(vars) - 1:
#                if state == 0:
#                    current[1] = const0
#                else:
#                    current[1] = const1
#            else:
#                current = [vars[index], None, None]
#                stack.append(current)
#                index += 1
#        elif current[2] is None:
#            state += 1
#            if index == len(vars) - 1:
#                if state == 0:
#                    current[2] = const1
#                else:
#                    current[2] = const0
#            else:
#                if state > 1:
#                    current[2] = const0
#                else:
#                    current = [vars[index], None, None]
#                    stack.append(current)
#                    index += 1
#        else:
#            state -= 1
#            new_node = choice(*current)
#            stack.pop()
#            current = stack[-1]
#            index -= 1
#    return stack[-1]
#
#print(exactly_one(variables[:3]))
#  
# each team does one thing each week
#for ii in range(N):
#    for ww in range(M):
#        team = chr(ord('a')+ii)
#        components = [v for v in variables if team in v and str(ww) in v]
#        constraint = exactly_one(components)

# each game played exactly once
