import os
import sys
from typing import List, Optional

import pygame

from .deck import Deck
from .hand_evaluator import score_hand
from .cards import SUIT_COLORS, RANKS
from .jokers import Joker, ExtraMultiplierJoker, AceHighJoker


class PokerGame:
    """Simple Balatro-like poker game skeleton using Pygame."""

    BG_COLOR = (20, 120, 20)
    CARD_COLOR = (255, 255, 255)
    TEXT_COLOR = (0, 0, 0)
    GLOW_COLOR = (255, 255, 0)
    PANEL_COLOR = (30, 30, 30)
    BLUE = (50, 100, 200)
    RED = (200, 50, 50)

    def __init__(self) -> None:
        self.deck = Deck()
        self.hand: List = self.deck.draw(8)
        self.selected: set[int] = set()
        self.card_rects: List[pygame.Rect] = []
        self.screen = None
        self.font = None
        self.small_font = None
        self.jokers: List[Joker] = [ExtraMultiplierJoker(), AceHighJoker()]

        # round state
        self.goal = 300
        self.round_score = 0
        self.base_chips = 0
        self.multiplier = 0
        self.hands_left = 4
        self.discards_left = 3
        self.round = 1
        self.money = 0

        # button rects (set in draw_ui)
        self.play_button: Optional[pygame.Rect] = None
        self.discard_button: Optional[pygame.Rect] = None
        self.sort_rank_button: Optional[pygame.Rect] = None
        self.sort_suit_button: Optional[pygame.Rect] = None

    def start(self) -> None:
        pygame.init()
        size = (800, 600)
        # allow running without a display (useful for tests)
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":
            os.environ["SDL_AUDIODRIVER"] = "dummy"
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Poker Game")
        # use a font with broad glyph support
        self.font = pygame.font.SysFont("freesansbold", 36)
        self.small_font = pygame.font.SysFont("freesansbold", 24)
        self.game_loop()

    def draw_hand(self) -> None:
        if not self.screen:
            return
        self.screen.fill(self.BG_COLOR)
        self.card_rects = []
        n = len(self.hand)
        center_x = self.screen.get_width() // 2
        base_y = 300
        curvature = 5
        angle_step = 10
        offset_x = 60
        card_w, card_h = 80, 120
        mouse_pos = pygame.mouse.get_pos()
        for i, card in enumerate(self.hand):
            angle = (i - (n - 1) / 2) * angle_step
            x = center_x + (i - (n - 1) / 2) * offset_x
            y = base_y + curvature * (i - (n - 1) / 2) ** 2
            if i in self.selected:
                y -= 30
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_surf.fill(self.CARD_COLOR)
            color = SUIT_COLORS[card.suit]
            pygame.draw.rect(card_surf, color, card_surf.get_rect(), 3)
            self._draw_card_contents(card_surf, card, color)
            rotated = pygame.transform.rotate(card_surf, angle)
            rect = rotated.get_rect(center=(x, y))
            hovered = rect.collidepoint(mouse_pos)
            if hovered:
                # redraw with glow
                card_surf2 = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                card_surf2.fill(self.CARD_COLOR)
                self._draw_card_contents(card_surf2, card, color)
                pygame.draw.rect(card_surf2, self.GLOW_COLOR, card_surf2.get_rect(), 6)
                rotated = pygame.transform.rotate(card_surf2, angle)
                rect = rotated.get_rect(center=(x, y))
            self.card_rects.append(rect)
            self.screen.blit(rotated, rect)

        self.draw_ui()
        pygame.display.flip()

    def _draw_card_contents(self, surf: pygame.Surface, card, color):
        """Render rank text and suit symbol onto a card surface."""
        rank_txt = self.font.render(card.rank, True, color)
        surf.blit(rank_txt, (5, 5))
        # center suit symbol drawn via shapes
        cx, cy = surf.get_width() // 2, surf.get_height() // 2 + 10
        self._draw_suit_symbol(surf, card.suit, (cx, cy))

    def _draw_suit_symbol(self, surf: pygame.Surface, suit: str, center: tuple[int, int]) -> None:
        x, y = center
        size = 15
        color = SUIT_COLORS[suit]
        if suit == '♦':
            pygame.draw.polygon(surf, color, [(x, y - size), (x + size, y), (x, y + size), (x - size, y)])
        elif suit == '♥':
            pygame.draw.circle(surf, color, (x - size // 2, y - size // 3), size // 2)
            pygame.draw.circle(surf, color, (x + size // 2, y - size // 3), size // 2)
            pygame.draw.polygon(surf, color, [(x - size, y - size // 3), (x + size, y - size // 3), (x, y + size)])
        elif suit == '♠':
            pygame.draw.polygon(surf, color, [(x - size, y), (x + size, y), (x, y - size)])
            pygame.draw.circle(surf, color, (x - size // 2, y + size // 3), size // 2)
            pygame.draw.circle(surf, color, (x + size // 2, y + size // 3), size // 2)
            pygame.draw.rect(surf, color, (x - size // 4, y + size // 3, size // 2, size))
        else:  # clubs
            pygame.draw.circle(surf, color, (x, y - size // 2), size // 2)
            pygame.draw.circle(surf, color, (x - size // 2, y + size // 6), size // 2)
            pygame.draw.circle(surf, color, (x + size // 2, y + size // 6), size // 2)
            pygame.draw.rect(surf, color, (x - size // 4, y + size // 6, size // 2, size))

    def draw_ui(self) -> None:
        """Draw score boxes, buttons, and deck info."""
        if not self.screen:
            return
        screen = self.screen
        # left panel
        panel = pygame.Rect(20, 20, 180, 560)
        pygame.draw.rect(screen, self.PANEL_COLOR, panel)
        y = panel.y + 10
        goal_txt = self.small_font.render(f"Score at least {self.goal}", True, (255, 255, 255))
        screen.blit(goal_txt, (panel.x + 10, y))
        y += 30
        rs_txt = self.small_font.render(f"Round score: {self.round_score}", True, (255, 255, 255))
        screen.blit(rs_txt, (panel.x + 10, y))
        y += 40
        # base and multiplier boxes
        base_rect = pygame.Rect(panel.x + 10, y, 70, 50)
        mult_rect = pygame.Rect(panel.x + 90, y, 70, 50)
        pygame.draw.rect(screen, self.BLUE, base_rect)
        pygame.draw.rect(screen, self.RED, mult_rect)
        base_txt = self.font.render(str(self.base_chips), True, (255, 255, 255))
        mult_txt = self.font.render(str(self.multiplier), True, (255, 255, 255))
        screen.blit(base_txt, base_rect.move(15, 5))
        screen.blit(mult_txt, mult_rect.move(15, 5))
        y += 70
        hands_txt = self.small_font.render(f"Hands: {self.hands_left}", True, (255, 255, 255))
        disc_txt = self.small_font.render(f"Discards: {self.discards_left}", True, (255, 255, 255))
        screen.blit(hands_txt, (panel.x + 10, y))
        y += 25
        screen.blit(disc_txt, (panel.x + 10, y))
        y += 40
        money_txt = self.small_font.render(f"$ {self.money}", True, (255, 255, 0))
        screen.blit(money_txt, (panel.x + 10, y))
        y += 40
        round_txt = self.small_font.render(f"Round {self.round}", True, (255, 255, 255))
        screen.blit(round_txt, (panel.x + 10, y))

        # buttons bottom center
        self.play_button = pygame.Rect(280, 520, 120, 40)
        self.discard_button = pygame.Rect(420, 520, 120, 40)
        pygame.draw.rect(screen, self.BLUE, self.play_button)
        pygame.draw.rect(screen, self.RED, self.discard_button)
        play_txt = self.small_font.render("Play Hand", True, (255, 255, 255))
        disc_txt = self.small_font.render("Discard", True, (255, 255, 255))
        screen.blit(play_txt, (self.play_button.x + 10, self.play_button.y + 10))
        screen.blit(disc_txt, (self.discard_button.x + 20, self.discard_button.y + 10))

        self.sort_rank_button = pygame.Rect(340, 470, 80, 30)
        self.sort_suit_button = pygame.Rect(430, 470, 80, 30)
        pygame.draw.rect(screen, (100, 100, 100), self.sort_rank_button)
        pygame.draw.rect(screen, (100, 100, 100), self.sort_suit_button)
        sr_txt = self.small_font.render("Rank", True, (255, 255, 255))
        ss_txt = self.small_font.render("Suit", True, (255, 255, 255))
        screen.blit(sr_txt, (self.sort_rank_button.x + 15, self.sort_rank_button.y + 5))
        screen.blit(ss_txt, (self.sort_suit_button.x + 20, self.sort_suit_button.y + 5))

        # deck info bottom right
        deck_rect = pygame.Rect(screen.get_width() - 110, screen.get_height() - 150, 80, 120)
        pygame.draw.rect(screen, self.CARD_COLOR, deck_rect)
        pygame.draw.rect(screen, (0, 0, 0), deck_rect, 2)
        deck_txt = self.small_font.render(f"{len(self.deck)}/52", True, (0, 0, 0))
        screen.blit(deck_txt, deck_rect.move(5, 5))

        # selected hand preview
        preview_y = 50
        if len(self.selected) == 5:
            cards = [self.hand[i] for i in sorted(self.selected)]
            name, base, mult, card_sum, total = score_hand(cards)
            chips = base + card_sum
            for joker in self.jokers:
                chips, mult = joker.apply(cards, chips, mult)
            preview = f"{name}: {chips} x {mult} = {chips * mult}"
        else:
            preview = "Select 5 cards"
        preview_txt = self.small_font.render(preview, True, (255, 255, 255))
        screen.blit(preview_txt, (220, preview_y))

    def game_loop(self) -> None:
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.play_button and self.play_button.collidepoint(event.pos):
                        self.play_selected_hand()
                    elif self.discard_button and self.discard_button.collidepoint(event.pos):
                        self.discard_selected_cards()
                    elif self.sort_rank_button and self.sort_rank_button.collidepoint(event.pos):
                        self.hand.sort(key=lambda c: RANKS.index(c.rank))
                        self.selected.clear()
                    elif self.sort_suit_button and self.sort_suit_button.collidepoint(event.pos):
                        self.hand.sort(key=lambda c: (c.suit, RANKS.index(c.rank)))
                        self.selected.clear()
                    else:
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

    def replace_selected(self) -> None:
        if not self.selected:
            return
        indices = sorted(self.selected)
        needed = len(indices)
        if len(self.deck) < needed:
            self.deck = Deck()
        new_cards = self.deck.draw(needed)
        for idx, card in zip(indices, new_cards):
            self.hand[idx] = card
        self.selected.clear()

    def play_selected_hand(self) -> None:
        if len(self.selected) != 5 or self.hands_left <= 0:
            return
        cards = [self.hand[i] for i in sorted(self.selected)]
        name, base, mult, card_sum, _ = score_hand(cards)
        chips = base + card_sum
        for joker in self.jokers:
            chips, mult = joker.apply(cards, chips, mult)
        total = chips * mult
        self.base_chips = chips
        self.multiplier = mult
        self.round_score += total
        self.hands_left -= 1
        self.replace_selected()

    def discard_selected_cards(self) -> None:
        if not self.selected or self.discards_left <= 0:
            return
        self.discards_left -= 1
        self.replace_selected()


def main() -> int:
    game = PokerGame()
    game.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
