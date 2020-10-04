# -*- coding: utf-8 -*-
"""python card and deck"""

import collections
import random

Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = ['spades', 'diamonds', 'clubs', 'hearts']

    def __init__(self):
        self._cards = [
            Card(rank, suit)
            for suit in self.suits
            for rank in self.ranks
        ]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, item):
        return self._cards[item]


deck = FrenchDeck()

print(len(deck))
print(deck[:3])

cnt = 0
for card in deck:
    cnt += 1
if cnt == len(deck):
    print('done loop')

test_card = Card('7', 'diamonds')
print(test_card in deck)

print(random.choice(deck))
print(random.choice(deck))
print(random.choice(deck))


class FrenchDeckAdv(FrenchDeck):

    def __contains__(self, item):
        return item in self._cards

    def __setitem__(self, key, value):
        self._cards[key] = value


deck = FrenchDeckAdv()

print(test_card in deck)

random.shuffle(deck)
print(deck[:3])
