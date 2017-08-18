import random
import time
from math import isinf
try: import graphviz
except ImportError: pass

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
                constraint[ii] = variable(left, right)
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
                constraint[ii] =variable(left, right)
    return constraint[0]

def viz(graph, name):
    counter = 0
    nodes = [graph]
    try:
        dot = graphviz.Digraph(name)
    except NameError: return
    while len(nodes) > 0:
        next_nodes = set()
        for node in nodes:
            #dot.node(str(id(node)), "{}.{}".format(node.name, node.rank))
            dot.node(str(id(node)), "{}".format(node.name))
            counter += 1
            try:
                if node.if0 is const0:
                    #zero = str(random.random())
                    #dot.node(zero, "0")
                    #dot.edge(str(id(node)), zero, label='0')
                    pass
                elif node.if0 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='0')
                else:
                    dot.edge(str(id(node)), str(id(node.if0)), label='0')
                    next_nodes.add(node.if0)

                if node.if1 is const0:
                    #zero = str(random.random())
                    #dot.node(zero, "0")
                    #dot.edge(str(id(node)), zero, label='1')
                    pass
                elif node.if1 is const1:
                    one = str(random.random())
                    dot.node(one, "1")
                    dot.edge(str(id(node)), one, label='1')
                else:
                    dot.edge(str(id(node)), str(id(node.if1)), label='1')
                    next_nodes.add(node.if1)
            except AttributeError: pass
        nodes = next_nodes

    print("{} nodes in {}".format(counter, name))
    dot.render(name, view=False)

# A Possibly More Realistic Example?
# Let's say we want to do a round-robin tournament among
# N teams across M days.  Each team may play at most once
# in a day.

# Combining the loops helps because of the overlapping
# variables.  But I think we can do better.

def make_variables(teams, days):
    variables = list()
    rank = 0
    for dd in range(days):
        for ii in range(teams):
            for jj in range(ii+1,teams):
                name = "{}{}{}".format(chr(ord('a')+ii), chr(ord('a')+jj), dd)
                variables.append(Variable(name, rank))
                rank += 1
            name = "{}B{}".format(chr(ord('a')+ii), dd)
            variables.append(Variable(name, rank))
            rank += 1
    return variables

def make_constraint_graph(teams, days, variables):
    all_components = list()
    for tt in range(teams):
        for dd in range(days):
            team = str(chr(ord('a')+tt))

            components = sorted([v for v in variables if team in v.name and str(dd) in v.name], key=lambda v: v.rank)
            #print("(tt, dd) ({}, {}): {}".format(tt, dd, components))
            all_components.append(components)

        for uu in range(tt+1,teams):
            match = "{}{}".format(chr(ord('a')+tt), chr(ord('a')+uu))
            components = sorted([v for v in variables if match in v.name], key=lambda v: v.rank)
            #print("(tt, uu) ({}, {}): {}".format(tt, uu, components))
            all_components.append(components)

    all_components.sort(key=lambda c: c[0].rank, reverse=True)
    constraint = const1
    components_considered = set()
    try:
        while len(all_components) > 0:
            overlaps = [len(components_considered.intersection(components)) for components in all_components]
            biggest_overlap = max(overlaps)
            components_having_biggest_overlap = [c for c,o in zip(all_components, overlaps) if o == biggest_overlap]
            chbo = components_having_biggest_overlap
            # break tie by taking shortest
            lengths = [len(c) for c in chbo]
            shortest = min(lengths)
            shortest_chbos = [c for c,n in zip(chbo, lengths) if n == shortest]
            # break tie by taking last-ranked first variable
            ranks = [c[0].rank for c in shortest_chbos]
            maxrank = max(ranks)
            last_ranked = [c for c,r in zip(shortest_chbos, ranks) if r == maxrank]
            # if there's still a tie, just take the first one
            components = last_ranked[0]
            only_one = at_most_n(1, components)(const0, at_least_n(1, components))
            constraint = constraint(const0, only_one)
            all_components = [c for c in all_components if c is not components]
            print("{}: {}".format(len(all_components), len(build_node._memos)))
    except KeyboardInterrupt:
        pass
    return constraint

def make_constraint_graph_binary(teams, days, variables):
    started = time.time()
    constraints = list()
    for tt in range(teams):
        for dd in range(days): # team may do only one thing in a day
            team = str(chr(ord('a')+tt))
            components = sorted([v for v in variables if team in v.name and str(dd) in v.name], key=lambda v: v.rank)
            only_one = at_most_n(1, components)(const0, at_least_n(1, components))
            constraints.append(only_one)

        for uu in range(tt+1,teams): # each match must happen exactly once
            match = "{}{}".format(chr(ord('a')+tt), chr(ord('a')+uu))
            components = sorted([v for v in variables if match in v.name], key=lambda v: v.rank)
            only_one = at_most_n(1, components)(const0, at_least_n(1, components))
            constraints.append(only_one)

    while len(constraints) > 1:
        merged = list()
        for ii in range(len(constraints) // 2):
            print("{}.{}: {} ({:.1f})".format(len(constraints), len(merged), len(build_node._memos), time.time() - started))
            merged.append(constraints[2*ii](const0, constraints[2*ii+1]))
        if 2 * len(merged) < len(constraints): # len(constraints) is odd
            #merged[-1] = choice(merged[-1], const0, constraints[-1]) # make everything even again
            #merged = [choice(c, const0, constraints[-1]) for c in merged] # this takes the odd one into all
            merged.insert(0, constraints[-1]) # this rotates the oddness
            #merged.append(constraints[-1])
        constraints = merged

    print("{}: {} ({:.1f}s)".format(len(constraints), len(build_node._memos), time.time() - started))
    return constraints[0]

build_node._memos.clear()
teams = 6
days = 5
variables = make_variables(teams, days)
print("{} variables: {}".format(len(variables), variables))
constraint_graph = make_constraint_graph_binary(teams, days, variables)
cgtext = repr(constraint_graph)
print("constraint graph {}".format(len(cgtext)))
name = "both_constraints_{}_{}".format(teams, days)
with open("{}.{}".format(name, "text"), 'w') as fp:
    fp.write(cgtext)
    fp.write("\n")
viz(constraint_graph, name)
