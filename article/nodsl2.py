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
M = 3

variables = list()
rank = 0
for dd in range(M):
    for ii in range(N):
        for jj in range(ii+1,N):
            name = "{}{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj), dd)
            variables.append(variable(name, rank))
            rank += 1
        name = "{}B{}".format(chr(ord('a')+ii), dd)
        variables.append(variable(name, rank))
        rank += 1

constraints = list()

def at_least_one(vars):
    # early return for trivial failure
    if len(vars) == 0: return const0

    # if only one variable, success on right branch, failure on the left
    constraint = vars.pop()
    while len(vars) > 0:
        constraint = choice(vars.pop(), constraint, const1)

    return constraint

def at_least_n(limit, vars):
    nvars = len(vars)
    # trivial failure
    if nvars < limit: return const0
    # trivial success
    if limit <= 0: return const1
    vars = sorted(vars, key=lambda v: v.rank)
    constraint = [const0 for _ in range(limit)]
    constraint.append(const1)

    index = nvars - 1
    while index >= 0:
        variable = vars[index]
        index -= 1
        for ii in range(len(constraint) - 1):
            left = constraint[ii]
            right = constraint[ii+1]
            if left is not right:
                constraint[ii] = choice(variable, left, right)
    return constraint[0]

def at_most_n(limit, vars):
    nvars = len(vars)
    # trivial failure
    if limit < 0: return const0
    # trivial success
    if limit > nvars: return const1
    vars = sorted(vars, key=lambda v: v.rank)
    constraint = [const1 for _ in range(limit + 1)]
    constraint.append(const0)
    index = nvars - 1
    while index >= 0:
        variable = vars[index]
        index -= 1
        for ii in range(len(constraint) - 1):
            left = constraint[ii]
            right = constraint[ii+1]
            if left is not right:
                constraint[ii] = choice(variable, left, right)
    return constraint[0]
am = at_most_n(3, variables[:8])
al = at_least_n(3, variables[:8])
print(am, al)
print(choice(am, const0, al))



def viz3(graph, name):
    nodes = [graph]
    dot = graphviz.Digraph(name)
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

    dot.render(name, view=False)
    print(name)
try:
    import graphviz
    viz3(choice(am, const0, al), "exactly_3_of_8")
except ImportError:
    pass

constraint = const1

for ii in range(N):
    for dd in range(M):
        print("team {} day {} nodes {}".format(ii, dd, len(choice_nodes)))
        team = str(chr(ord('a')+ii))
        components = [v for v in variables if team in v.name and str(dd) in v.name]
        only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
        constraint = choice(constraint, const0, only_one)

no_double_booking = constraint
try:
    import graphviz
    name = "no_double_booking"
    viz3(no_double_booking, name)
except ImportError: pass

constraint = const1
# Games happen exactly once
for ii in range(N):
    for jj in range(ii+1,N):
        match = "{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj))
        print("match {} nodes {}".format(match, len(choice_nodes)))
        components = [v for v in variables if match in v.name]
        only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
        constraint = choice(constraint, const0, only_one)

play_exactly_once = constraint

try:
    import graphviz
    name = "play_exactly_once"
    viz3(play_exactly_once, name)
except ImportError: pass

both_constraints = choice(no_double_booking, const0, play_exactly_once)
try:
    import graphviz
    name = "both_constraints"
    viz3(both_constraints, name)
except ImportError: pass

print(both_constraints)

# The really interesting thing is that we can generate a
# BDD that has all of the feasible solutions built into it.
# And we can prove the feasibility of the problem -- indeed
# the fact that the BDD doesn't collapse to const0 shows
# that it's feasible.  Furthermore, we can generate feasible
# solutions just by walking the graph.  We only backtrack if
# we want to generate another feasible solution, because we
# never descend into an infeasible branch, because there's no
# such thing.  Infeasible branches collapse to const0.

# The bad news is performance.  Unless we can keep the
# constraints really tight, the graph blows up.


choice_nodes.clear()

N = 5
M = 3

variables = list()
rank = 0
for dd in range(M):
    for ii in range(N):
        for jj in range(ii+1,N):
            name = "{}{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj), dd)
            variables.append(variable(name, rank))
            rank += 1
        name = "{}B{}".format(chr(ord('a')+ii), dd)
        variables.append(variable(name, rank))

constraint = const1

class Zeero(Exception): pass

try:
    for ii in range(N):
        for dd in range(M):
            team = str(chr(ord('a')+ii))
            print("team {} day {} nodes {}".format(team, dd, len(choice_nodes)))
            components = [v for v in variables if team in v.name and str(dd) in v.name]
            only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
            new_constraint = choice(constraint, const0, only_one)
            if new_constraint is const0:
                raise Zeero
            else:
                constraint = new_constraint

        for jj in range(ii+1,N):
            match = "{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj))
            print("match {} nodes {}".format(match, len(choice_nodes)))
            components = [v for v in variables if team in v.name and str(dd) in v.name]
            only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
            new_constraint = choice(constraint, const0, only_one)
            if new_constraint is const0:
                raise Zeero
            else:
                constraint = new_constraint
except Zeero:
    print("FAILED")
    try:
        import graphviz
        name = "both_constraints_{}_{}".format(M, N)
        viz3(only_one, "only_one")
    except ImportError: pass

try:
    import graphviz
    name = "both_constraints_{}_{}".format(M, N)
    viz3(constraint, name)
except ImportError: pass


# Combining the loops helps because of the overlapping
# variables.  But I think we can do better.

choice_nodes.clear()

def make_problem(teams, days):
    variables = list()
    rank = 0
    for dd in range(M):
        for ii in range(N):
            for jj in range(ii+1,N):
                name = "{}{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj), dd)
                variables.append(variable(name, rank))
                rank += 1
            name = "{}B{}".format(chr(ord('a')+ii), dd)
            variables.append(variable(name, rank))
    return variables

N = 6
M = 6
variables = make_problem(N, M)

all_components = list()
for ii in range(N):
    for dd in range(M):
        team = str(chr(ord('a')+ii))
        components = [v for v in variables if team in v.name and str(dd) in v.name]
        all_components.append(components)

    for jj in range(ii+1,N):
        match = "{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj))
        components = [v for v in variables if team in v.name and str(dd) in v.name]
        all_components.append(components)

all_components.sort(key=lambda c: c[0].rank, reverse=True)
constraint = const1
for components in all_components:
    only_one = choice(at_most_n(1, components), const0, at_least_n(1, components))
    constraint = choice(constraint, const0, only_one)
try:
    import graphviz
    name = "both_constraints_{}_{}".format(M, N)
    viz3(constraint, name)
except ImportError: pass

# Oh heck yes.  That's blazingly faster.  Moral of the
# story: build the graph in a way that helps standardize it.

exit()

def shuffle(index_graph, selected_graph, exit_):
    """ exit_ is const0 or const1 """
    # so if the exit_ is const0, then the resulting graph
    # will just have the const0 exit_s from index_graph.
    if index_graph is exit_: return selected_graph
    if index_graph in (const0, const1): return const0 # not informative
    if selected_graph is exit_: return index_graph

    igrank = index_graph.rank
    sgrank = selected_graph.rank
    levels = list()
    if igrank < sgrank:
        levels.append([variable(index_graph.name, igrank)])

    # for blah blah in levels[-1] do stuff




def iteratively_standardize(index, graph_a, graph_b):
    # build left graph
    left = shuffle(index, graph_a, const0)
    # build right graph
    right = shuffle(index, graph_b, const1)
    # assemble full graph

