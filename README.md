# Poker Game

A very early prototype of a Balatro-inspired poker game built with Python and Pygame.

## Running the game

Install dependencies and run the game:

```bash
pip install -r requirements.txt
python main.py
```

Click cards to select up to five from the eight dealt. Use the **Play Hand**
button to score the selection or **Discard** to redraw the chosen cards.
Buttons allow sorting the hand by rank or suit. Cards fan out in an inverted
arc; hovering applies a soft glow and clicking lifts them to show selection.

The left panel tracks the round score, goal, remaining hands, discards, and
shows the base chip and multiplier values of the last played hand. A simple
deck display in the corner shows how many cards remain. A couple of sample
jokers apply bonus chips or multipliers to the scored hand.
