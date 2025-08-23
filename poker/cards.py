# Classic suit glyphs for broad font support
SUITS = ['♠', '♥', '♦', '♣']
SUIT_COLORS = {
    '♠': (0, 0, 0),
    '♣': (0, 0, 0),
    '♥': (200, 0, 0),
    '♦': (200, 0, 0),
}
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i for i, r in enumerate(RANKS, start=2)}

class Card:
    """Represents a standard playing card."""

    def __init__(self, rank: str, suit: str):
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank
        self.suit = suit

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"Card(rank={self.rank}, suit={self.suit})"

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"
