import os
import sys
from typing import List

import pygame

from .deck import Deck
from .hand_evaluator import score_hand
from .cards import SUIT_COLORS
from .jokers import Joker, ExtraMultiplierJoker, AceHighJoker

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
        self.jokers: List[Joker] = [ExtraMultiplierJoker(), AceHighJoker()]

    def start(self) -> None:
        pygame.init()
        size = (800, 600)
        # allow running without a display (useful for tests)
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":
            os.environ["SDL_AUDIODRIVER"] = "dummy"
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Poker Game")
        self.font = pygame.font.SysFont("comicsansms", 36)
        self.game_loop()

    def draw_hand(self) -> None:
        if not self.screen:
            return
        self.screen.fill(self.BG_COLOR)
        self.card_rects = []
        n = len(self.hand)
        center_x = self.screen.get_width() // 2
        base_y = 350
        angle_step = 10
        offset_x = 60
        card_w, card_h = 80, 120
        for i, card in enumerate(self.hand):
            angle = (i - (n - 1) / 2) * angle_step
            x = center_x + (i - (n - 1) / 2) * offset_x
            y = base_y
            if i in self.selected:
                y -= 30
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_surf.fill(self.CARD_COLOR)
            color = SUIT_COLORS[card.suit]
            pygame.draw.rect(card_surf, color, card_surf.get_rect(), 3)
            txt = self.font.render(str(card), True, color)
            txt_rect = txt.get_rect(center=(card_w / 2, card_h / 2))
            card_surf.blit(txt, txt_rect)
            rotated = pygame.transform.rotate(card_surf, angle)
            rect = rotated.get_rect(center=(x, y))
            self.card_rects.append(rect)
            self.screen.blit(rotated, rect)

        info_y = 50
        if len(self.selected) == 5:
            cards = [self.hand[i] for i in sorted(self.selected)]
            name, base, mult, card_sum, _ = score_hand(cards)
            chips = base + card_sum
            for joker in self.jokers:
                chips, mult = joker.apply(cards, chips, mult)
            total = chips * mult
            msg = f"{name}: {chips} x {mult} = {total}"
        else:
            msg = "Select 5 cards"
        score_txt = self.font.render(msg, True, (255, 255, 255))
        self.screen.blit(score_txt, (50, info_y))
        info_y += 40
        joker_names = ", ".join(j.name for j in self.jokers)
        joker_txt = self.font.render(f"Jokers: {joker_names}", True, (255, 255, 255))
        self.screen.blit(joker_txt, (50, info_y))
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
                    for i in reversed(range(len(self.card_rects))):
                        rect = self.card_rects[i]
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
