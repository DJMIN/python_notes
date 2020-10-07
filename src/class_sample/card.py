# -*- coding: utf-8 -*-
"""python card and deck"""

import collections
import random

Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    """French Deck with 13 * 4 = 52 cards"""
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = ['spades', 'diamonds', 'clubs', 'hearts']

    def __init__(self):
        """make all 52 cards and set protected"""
        self._cards = [
            Card(rank, suit)
            for suit in self.suits
            for rank in self.ranks
        ]

    def __len__(self):
        """set length of deck as count of cards"""
        return len(self._cards)

    def __getitem__(self, item):
        """allow indexing like deck[0]"""
        return self._cards[item]


# create deck instance
deck = FrenchDeck()

# try len(), indexing and slicing
print(len(deck))
print(deck[:3])

# iter deck is allowed by __getitem__ and __len__
cnt = 0
for card in deck:
    cnt += 1
if cnt == len(deck):
    print('done loop')

# in clause call __contains__
# but when __contains__ is not defined, python use iter to find
# so when __getitem__ and __len__ is defined, in clause is allowed
test_card = Card('7', 'diamonds')
print(test_card in deck)

# random.choice also works due to definition of __getitem__ and __len__
print(random.choice(deck))
print(random.choice(deck))
print(random.choice(deck))


class FrenchDeckAdv(FrenchDeck):
    """advanced French Deck with more magic methods"""

    def __contains__(self, item):
        """make in clause more straightforward and efficient"""
        return item in self._cards

    def __setitem__(self, key, value):
        """allow set item for shuffle"""
        self._cards[key] = value


deck = FrenchDeckAdv()

# now in clause becomes more straightforward
print(test_card in deck)

# random.shuffle is now allowed due to __setitem__
random.shuffle(deck)
print(deck[:3])
