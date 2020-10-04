# -*- coding: utf-8 -*-
"""doc string"""

import math


class Vector2D:
    __slots__ = ['x', 'y']

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector({repr(self.x)}, {repr(self.y)})'

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2D(x, y)

    def __mul__(self, scalar):
        x = self.x * scalar
        y = self.y * scalar
        return Vector2D(x, y)


v1 = Vector2D(2, 1)
v2 = Vector2D(2, 4)
print(v1 + v2)

v = Vector2D(3, 4)
print(abs(v))

print(v * 3)

print(bool(v))

vn = Vector2D()
print(bool(vn))


class Vector2DAdv(Vector2D):

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return self.x * other.x + self.y * other.y
        return super().__mul__(other)

    def __neg__(self):
        return Vector2DAdv(- self.x, - self.y)

    def __lt__(self, other):
        return abs(self) < abs(other)


v1 = Vector2DAdv(2, 1)
v2 = Vector2DAdv(2, 4)
print(v1 * v2)
print(v1 < v2)

v = Vector2DAdv(3, 4)
print(- v)
