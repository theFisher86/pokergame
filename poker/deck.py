from __future__ import annotations

import random
from typing import List

from .cards import Card, SUITS, RANKS


class Deck:
    """Represents a deck of 52 playing cards."""

    def __init__(self) -> None:
        self.cards: List[Card] = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Card]:
        if n > len(self.cards):
            raise ValueError("Not enough cards left in the deck")
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn

    def __len__(self) -> int:
        return len(self.cards)
