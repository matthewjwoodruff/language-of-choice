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

# constant nodes are terminal -- they do not have if0 or if1
ConstantNode = namedtuple("ConstantNode", (
    'name',
    'rank',
    'value'))
ConstantNode.__repr__ = lambda n: n.name

def fancy(node):
    try:
        if node.if0.value == 0 and node.if1.value == 1:
            return node.name
        elif node.if1.value == 0 and node.if0.value == 1:
            return "~{}".format(node.name)
    except AttributeError: pass
    return "{}({},{})".format(node.name, repr(node.if0), repr(node.if1))

# choice nodes do not have a value in the absolute sense,
# only in the context of an environment
ChoiceNode = namedtuple("ChoiceNode", (
    'name',
    'rank',
    'if0',
    'if1' ))
ChoiceNode.__repr__ = fancy

const0 = ConstantNode('0', inf, 0)
const1 = ConstantNode('1', inf, 1)

def variable(name, rank):
    return ChoiceNode(name, rank, const0, const1)

def collapse_irrelevant(index, if0, if1):
    if if0 is if1: return if0
    return ChoiceNode(index.name, index.rank, if0, if1)

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
        return ChoiceNode(node.name, node.rank, left, right)

def choice(index, if0, if1):
    try:
        if if0.value == 0 and if1.value == 1:
            return index
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
p = variable('p', 2)

import sys
print(choice(p,a,b))
