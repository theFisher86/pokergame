import os
import sys
from typing import List

import pygame

from .deck import Deck
from .hand_evaluator import evaluate_hand


class PokerGame:
    """Simple Balatro-like poker game skeleton using Pygame."""

    BG_COLOR = (20, 120, 20)
    CARD_COLOR = (255, 255, 255)
    TEXT_COLOR = (0, 0, 0)

    def __init__(self) -> None:
        self.deck = Deck()
        self.hand: List = self.deck.draw(5)
        self.screen = None
        self.font = None

    def start(self) -> None:
        pygame.init()
        size = (800, 600)
        # allow running without a display (useful for tests)
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":
            os.environ["SDL_AUDIODRIVER"] = "dummy"
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Poker Game")
        self.font = pygame.font.SysFont(None, 36)
        self.game_loop()

    def draw_hand(self) -> None:
        if not self.screen:
            return
        self.screen.fill(self.BG_COLOR)
        spacing = 150
        start_x = 50
        y = 200
        for i, card in enumerate(self.hand):
            rect = pygame.Rect(start_x + i * spacing, y, 100, 140)
            pygame.draw.rect(self.screen, self.CARD_COLOR, rect)
            txt = self.font.render(str(card), True, self.TEXT_COLOR)
            txt_rect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_rect)
        # Display hand rank
        rank_idx, name = evaluate_hand(self.hand)
        rank_txt = self.font.render(name, True, (255, 255, 255))
        self.screen.blit(rank_txt, (50, 50))
        pygame.display.flip()

    def game_loop(self) -> None:
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if len(self.deck) < 5:
                        self.deck = Deck()
                    self.hand = self.deck.draw(5)
            self.draw_hand()
            clock.tick(30)
        pygame.quit()


def main() -> int:
    game = PokerGame()
    game.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
