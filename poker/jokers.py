from __future__ import annotations

from typing import List, Tuple

from .cards import Card


class Joker:
    """Base class for simple jokers that modify scoring."""

    name = "Joker"

    def apply(self, cards: List[Card], chips: int, mult: int) -> Tuple[int, int]:
        return chips, mult


class ExtraMultiplierJoker(Joker):
    name = "x2 Joker"

    def apply(self, cards: List[Card], chips: int, mult: int) -> Tuple[int, int]:
        return chips, mult + 2


class AceHighJoker(Joker):
    name = "Ace High"

    def apply(self, cards: List[Card], chips: int, mult: int) -> Tuple[int, int]:
        bonus = 10 * sum(1 for c in cards if c.rank == 'A')
        return chips + bonus, mult
