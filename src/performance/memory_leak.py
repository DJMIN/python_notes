# coding = utf-8
"""memory leak"""

import gc
import weakref

# memory leak means python cannot release memory when variable is out of usage
# python garbage collection depends on "reference count"
# when reference count of an object drop to zero, it will be collected, and its memory will be released

a = ['test']  # reference count of list ['test'] is 1 (a)
b = a  # reference count of list ['test'] is 2 (a & b)
a = 'new'  # a is redirect to string 'new', and reference count of list ['test'] drop to 1 (b)
del b  # variable b is deleted, reference count of list ['test'] drop to 0, collected

del a  # clean up variable a before starting next part

# memory leak occurs along with circular reference
# circular reference prevents reference count from dropping to 0
a = []  # variable a is pointed to space of empty list
a.append(a)  # space of list is pointed to its first element -> space of list itself
# now, space of list have to reference: variable a, and itself (as first element)
del a  # when variable a is deleted, reference count drop to 1, so the space of list will not be released
gc.collect()  # this argument will force collect the list even though its reference count is not 0


def prepare_list() -> list:
    output = []
    i = 0
    while i < 3E8:
        output.append('test_string')
        i += 1
    return output


# now begins an example, please check your memory usage throughout the example
msg = 'Check the change of memory usage.\nPress Enter to continue...\n'
print('Open your task manager to check memory usage.')
input(msg)
test_list = prepare_list()
print('A huge list of 3E8 elements is created.')
input(msg)
del test_list
print('The variable is deleted and the memory of list is released.')
input(msg)
test_list = prepare_list()
test_list.append(test_list)
print('The huge list is recreated, but this time, the list is appended to itself.')
input(msg)
del test_list
print('The variable is deleted but the memory is not released due to circular reference.')
input(msg)
gc.collect()
print('gc.collect() now release the memory to solve memory leak problem.')

# class attributes can also cause memory leak


class Node(object):
    def __init__(self):
        self.child = None


a = Node()  # Node instance 1, reference count 1 (a)
b = Node()  # Node instance 2, reference count 2 (b)
b.child = a  # Node instance 1, reference count 2 (a, b.child)
a.child = b  # Node instance 2, reference count 2 (b, a.child)
del a  # Node instance 1, reference count 1 (b.child) - cannot be released
del b  # Node instance 2, reference count 2 (a.child) - cannot be released
gc.collect()  # force collect

# usually call gc.collect() is not a good way to deal with memory leak
# a good way to avoid memory leak is to use weak reference (weakref)
a = Node()  # Node instance 1, reference count 1 (a)
b = Node()  # Node instance 2, reference count 2 (b)
b.child = weakref.proxy(a)  # Node instance 1, reference count 1 (weakref do not raise reference count)
a.child = weakref.proxy(b)  # Node instance 2, reference count 1 (weakref do not raise reference count)
del a  # Node instance 1, reference count 0 - released
del b  # Node instance 2, reference count 0 - released
