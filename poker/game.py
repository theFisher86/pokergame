import os
import sys
from typing import List

import pygame

from .deck import Deck
from .hand_evaluator import score_hand


class PokerGame:
    """Simple Balatro-like poker game skeleton using Pygame."""

    BG_COLOR = (20, 120, 20)
    CARD_COLOR = (255, 255, 255)
    TEXT_COLOR = (0, 0, 0)

    def __init__(self) -> None:
        self.deck = Deck()
        self.hand: List = self.deck.draw(8)
        self.selected: set[int] = set()
        self.card_rects: List[pygame.Rect] = []
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
        start_y = 100
        self.card_rects = []
        for i, card in enumerate(self.hand):
            row = i // 4
            col = i % 4
            rect = pygame.Rect(start_x + col * spacing, start_y + row * 200, 100, 140)
            self.card_rects.append(rect)
            pygame.draw.rect(self.screen, self.CARD_COLOR, rect)
            border_color = (255, 0, 0) if i in self.selected else (0, 0, 0)
            pygame.draw.rect(self.screen, border_color, rect, 3)
            txt = self.font.render(str(card), True, self.TEXT_COLOR)
            txt_rect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_rect)

        if len(self.selected) == 5:
            cards = [self.hand[i] for i in sorted(self.selected)]
            name, base, mult, card_sum, total = score_hand(cards)
            chips = base + card_sum
            msg = f"{name}: {chips} x {mult} = {total}"
        else:
            msg = "Select 5 cards"
        score_txt = self.font.render(msg, True, (255, 255, 255))
        self.screen.blit(score_txt, (50, 50))
        pygame.display.flip()

    def game_loop(self) -> None:
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if len(self.deck) < 8:
                        self.deck = Deck()
                    self.hand = self.deck.draw(8)
                    self.selected.clear()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(self.card_rects):
                        if rect.collidepoint(event.pos):
                            if i in self.selected:
                                self.selected.remove(i)
                            elif len(self.selected) < 5:
                                self.selected.add(i)
                            break
            self.draw_hand()
            clock.tick(30)
        pygame.quit()


def main() -> int:
    game = PokerGame()
    game.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
