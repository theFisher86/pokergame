from __future__ import annotations

from collections import Counter
from typing import Iterable, Tuple

from .cards import Card, RANK_VALUES

HAND_RANKS = [
    "High Card",
    "One Pair",
    "Two Pair",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush",
]

# Base chips and multipliers for each hand rank index
HAND_SCORES = [
    (5, 1),   # High Card
    (10, 2),  # One Pair
    (20, 2),  # Two Pair
    (30, 3),  # Three of a Kind
    (30, 4),  # Straight
    (35, 4),  # Flush
    (40, 4),  # Full House
    (60, 7),  # Four of a Kind
    (100, 8), # Straight Flush
]

# Card values used for scoring
CARD_SCORES = {
    **{str(n): n for n in range(2, 11)},
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 15,
}


def _is_straight(values: Iterable[int]) -> bool:
    values = sorted(values)
    return all(b - a == 1 for a, b in zip(values, values[1:]))


def evaluate_hand(cards: Iterable[Card]) -> Tuple[int, str]:
    """Evaluate a 5-card hand.

    Returns a tuple ``(rank_index, name)`` where ``rank_index`` is an integer
    where higher is better.
    """

    if len(list(cards)) != 5:
        raise ValueError("Hand evaluation requires exactly 5 cards")

    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]
    values = [RANK_VALUES[r] for r in ranks]

    rank_counter = Counter(ranks)
    counts = sorted(rank_counter.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = _is_straight(values)

    if is_straight and is_flush:
        return 8, HAND_RANKS[8]
    if counts[0] == 4:
        return 7, HAND_RANKS[7]
    if counts[0] == 3 and counts[1] == 2:
        return 6, HAND_RANKS[6]
    if is_flush:
        return 5, HAND_RANKS[5]
    if is_straight:
        return 4, HAND_RANKS[4]
    if counts[0] == 3:
        return 3, HAND_RANKS[3]
    if counts[0] == 2 and counts[1] == 2:
        return 2, HAND_RANKS[2]
    if counts[0] == 2:
        return 1, HAND_RANKS[1]
    return 0, HAND_RANKS[0]


def score_hand(cards: Iterable[Card]) -> Tuple[str, int, int, int, int]:
    """Return scoring details for a five-card hand.

    Returns a tuple ``(name, base, mult, card_sum, total)`` where ``total``
    equals ``(base + card_sum) * mult``.
    """

    rank_idx, name = evaluate_hand(cards)
    base, mult = HAND_SCORES[rank_idx]
    card_sum = sum(CARD_SCORES[c.rank] for c in cards)
    total = (base + card_sum) * mult
    return name, base, mult, card_sum, total
