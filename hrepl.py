#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''hrepl.py -- repl over hivex (Windows Registry) to navigate NTUSER.DAT and other hive files.

Classes:

tree { ...}

node { node ; children ; leaf? }

value { ... }

Search:

dfs , bfs

REPL Interface:

repl/s path &rest {
  .     show node
  ,     show children
  N RET down child
  ..    up
  ! S   sto
  @ S   rcl
  / S   seek
  : S   seek*
}

End.
'''

__author__ = "Johan Ponin"
__copyright__ = "Copyright 2022-, jnpn"
__credits__ = ["Johan Ponin"]
__license__ = "GPLv3"
__version__ = "0.0.1a0"
__maintainer__ = "Johan Ponin"
__email__ = "johan.ponin.pro@gmail.com"
__status__ = "Alpha"


import abc
import hivex
import datetime as d

class Tree(abc.ABC):

    @abc.abstractmethod
    def root(self):
        pass

    @abc.abstractmethod
    def hive(self):
        pass

    @abc.abstractmethod
    def node(self):
        pass

    @abc.abstractmethod
    def children(self):
        pass

    def dfs(self):
        yield self
        for c in self.children():
            yield from c.dfs()

    @abc.abstractmethod
    def is_leaf(self):
        pass

def take(iterator, n=10):
    while n:
        yield next(iterator)
        n -= 1

def find(tree, pred):
    '''
    import re
    import pprint
    >>> pprint.pprint(list(find(r, lambda n: re.match('oo', repr(n)))))
    '''
    return (n for n in tree.dfs() if pred(n))


def path(tree, seq):
    '''
    >>> path(tree, []) == tree
    >>> path(tree, [9]) == tree.children()[9]
    '''
    if seq:
        c = tree.children()
        a,*b = seq
        return path(c[a], b)
    else:
        return tree

def unroot(fn):
    hive = hivex.Hivex(fn)
    root = Node(hive.root(), hive)
    return root

class Node(Tree):

    def __init__(self, inode, hive):
        super().__init__()
        self.inode = inode
        self.HIVE = hive

    def hive(self):
        return self.HIVE

    def root(self):
        return self.hive().root()

    def node(self):
        return self.inode

    def from_inode(self, inode):
        return Node(inode, self.hive())

    def values(self):
        H = self.hive()
        return [Value(v, H) for v in H.node_values(self.node())]

    def children(self):
        H = self.hive()
        return [Node(n, H) for n in H.node_children(self.node())]

    # predicates

    def is_leaf(self):
        return len(self.children()) == 0

    def is_root(self):
        return self.node() == self.root()

    def leaf(self):
        if self.is_leaf():
            h = self.hive()
            n = self.node()
            return h.value_type(n)

    # display

    def __repr__(self):
        # name, leaf|node[, type, value]
        lim = 16
        name = self.hive().node_name(self.node())
        name = name if len(name) < lim else name[:14] + '...'
        num = self.node()
        kind = '.' if self.is_leaf() else ''
        return f'{name} {num}{kind}'

class Value():
    def __init__(self, value, hive):
        self.value = value
        self.hive = hive

    def __repr__(self):
        name = self.hive.value_key(self.value)
        type_ = '?' # self.hive.value_type(self.value)
        value = self.hive.value_value(self.value)
        return f'{name}::{type_} = {value}'

class Treewalk():
    def __init__(self, tree):
        self.tree = tree
        self.path = [tree]
        self.mem = {}

    def top(self):
        if len(self.path) > 0:
            return self.path[-1]

    def rst(self, mem_too=False):
        self.path = [self.tree]
        if mem_too:
            self.meme = {}

    def up(self):
        if len(self.path) > 0:
            return self.path.pop()

    def down(self, node):
        self.path.append(node)

    def sto(self, name):
        self.mem[name] = self.path[:]
        self.rst()

    def rcl(self, name):
        if name in self.mem:
            self.path = self.mem[name][:]

    def __repr__(self):
        a = f'path: {self.path}'
        b = f'-----'
        return '\n'.join([a,b])

def wepl(treewalk):
    '''
    .     show node
    ,     show children
    N RET down child
    ..    up
    ! S   sto
    @ S   rcl
    / S   seek
    : S   seek*
    '''
    while True:
        print(treewalk)
        ans = input("> ")
        if ans == ".":
            print(treewalk.top())
        if ans == ",":
            for i,n in enumerate(treewalk.top().children()):
                print(i,n)
        elif ans.isdigit():
            n = int(ans)
            c = treewalk.top().children()[n]
            treewalk.down(c)
        elif ans == "q":
            break
        elif ans == "r":
            treewalk.rst()
            print('soft reset')
        elif ans == "rr":
            treewalk.rst(mem_too=True)
            print('hard reset')
        elif ans == "..":
            c = treewalk.up()
            print(c)
        elif ans == "!":
            print('TODO sto "..."')
            name = '...'
            treewalk.sto(name)
        elif ans == "@":
            print('TODO rcl "..."')
            name = '...'
            treewalk.rcl(name)
        elif ans == "/ S":
            print('TODO', 'search first')
        elif ans == ": S":
            print('TODO', 'search all')
        else:
            print(ans, '?')

DEBUG = True

def debug(o):
    if DEBUG:
        print(o)

HIVEFN = "/media/noob/ACER320/Users/ACER/NTUSER.DAT"
H = hivex.Hivex(HIVEFN)

def main():
    '''    wepl(Treewalk(unroot(HIVEFN)))    '''
    r = unroot(HIVEFN)
    t = Treewalk(r)
    wepl(t)

############################## TEST

def test():
    r = unroot(HIVEFN)
    import ser
    x = ser.xml(r)
    return r,x
