import os
import sys
import random
from typing import List, Optional

import logging
import pygame

from .deck import Deck
from .hand_evaluator import score_hand
from .cards import SUIT_COLORS, RANKS, SUITS
from .jokers import Joker, ExtraMultiplierJoker, AceHighJoker
from .assets import svg_to_surface, FELT_SVG, CARD_BACK_SVG


class PokerGame:
    """Simple Balatro-like poker game skeleton using Pygame."""

    BG_COLOR = (20, 120, 20)
    CARD_COLOR = (255, 255, 255)
    TEXT_COLOR = (0, 0, 0)
    GLOW_COLOR = (255, 255, 255)
    PANEL_COLOR = (30, 30, 30)
    BLUE = (50, 100, 200)
    RED = (200, 50, 50)

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.deck = Deck()
        self.hand: List = self.deck.draw(8)
        self.selected: set[int] = set()
        self.card_rects: List[pygame.Rect] = []
        self.screen = None
        self.font = None
        self.small_font = None
        self.jokers: List[Joker] = [ExtraMultiplierJoker(), AceHighJoker()]

        if self.debug:
            logging.debug("Game initialized with hand: %s", self.hand)

        # round state
        self.goal = 300
        self.round_score = 0
        self.base_chips = 0
        self.multiplier = 0
        self.hands_left = 4
        self.discards_left = 3
        self.round = 1
        self.money = 0

        self.bg_tile: Optional[pygame.Surface] = None
        self.card_back: Optional[pygame.Surface] = None

        # button rects (set in draw_ui)
        self.play_button: Optional[pygame.Rect] = None
        self.discard_button: Optional[pygame.Rect] = None
        self.sort_rank_button: Optional[pygame.Rect] = None
        self.sort_suit_button: Optional[pygame.Rect] = None

    def start(self) -> None:
        if self.debug:
            logging.debug("Starting game loop")
        pygame.init()
        size = (800, 600)
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":
            os.environ["SDL_AUDIODRIVER"] = "dummy"
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Poker Game")
        self.font = pygame.font.SysFont("freesansbold", 36)
        self.small_font = pygame.font.SysFont("freesansbold", 24)
        self.bg_tile = svg_to_surface(FELT_SVG, (64, 64))
        self.card_back = svg_to_surface(CARD_BACK_SVG, (80, 120))
        try:
            self.game_loop()
        except Exception:
            logging.exception("Unhandled exception in game loop")
            raise

    def draw_hand(self) -> None:
        if not self.screen:
            return
        if self.bg_tile:
            for x in range(0, self.screen.get_width(), self.bg_tile.get_width()):
                for y in range(0, self.screen.get_height(), self.bg_tile.get_height()):
                    self.screen.blit(self.bg_tile, (x, y))
        else:
            self.screen.fill(self.BG_COLOR)
        self.card_rects = []
        n = len(self.hand)
        center_x = self.screen.get_width() // 2
        base_y = 300
        curvature = 5
        angle_step = 10
        offset_x = 40
        card_w, card_h = 80, 120
        mouse_pos = pygame.mouse.get_pos()
        for i, card in enumerate(self.hand):
            angle = (i - (n - 1) / 2) * angle_step
            x = center_x + (i - (n - 1) / 2) * offset_x
            y = base_y + curvature * (i - (n - 1) / 2) ** 2
            if i in self.selected:
                y -= 30
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, self.CARD_COLOR, card_surf.get_rect(), border_radius=8)
            color = SUIT_COLORS[card.suit]
            pygame.draw.rect(card_surf, color, card_surf.get_rect(), 3, border_radius=8)
            self._draw_card_contents(card_surf, card, color)
            rotated = pygame.transform.rotate(card_surf, angle)
            rect = rotated.get_rect(center=(x, y))
            hovered = rect.collidepoint(mouse_pos)
            if hovered:
                glow = self._apply_glow(card_surf)
                rotated = pygame.transform.rotate(glow, angle)
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

    def _apply_glow(self, surf: pygame.Surface) -> pygame.Surface:
        """Return a copy of the card surface with a white gradient glow."""
        w, h = surf.get_size()
        glow = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
        for i in range(10, 0, -1):
            alpha = int(15 * (11 - i))
            pygame.draw.rect(
                glow,
                (*self.GLOW_COLOR, alpha),
                pygame.Rect(10 - i, 10 - i, w + 2 * i, h + 2 * i),
                border_radius=8,
            )
        glow.blit(surf, (10, 10))
        return glow

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
        # left panel pinned to screen
        panel = pygame.Rect(20, 20, 180, screen.get_height() - 40)
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
        btn_y = screen.get_height() - 80
        self.play_button = pygame.Rect(screen.get_width() // 2 - 140, btn_y, 120, 40)
        self.discard_button = pygame.Rect(screen.get_width() // 2 - 10, btn_y, 120, 40)
        pygame.draw.rect(screen, self.BLUE, self.play_button)
        pygame.draw.rect(screen, self.RED, self.discard_button)
        play_txt = self.small_font.render("Play Hand", True, (255, 255, 255))
        disc_txt = self.small_font.render("Discard", True, (255, 255, 255))
        screen.blit(play_txt, (self.play_button.x + 10, self.play_button.y + 10))
        screen.blit(disc_txt, (self.discard_button.x + 20, self.discard_button.y + 10))

        sort_y = btn_y - 50
        self.sort_rank_button = pygame.Rect(screen.get_width() // 2 - 90, sort_y, 80, 30)
        self.sort_suit_button = pygame.Rect(screen.get_width() // 2 + 0, sort_y, 80, 30)
        pygame.draw.rect(screen, (100, 100, 100), self.sort_rank_button)
        pygame.draw.rect(screen, (100, 100, 100), self.sort_suit_button)
        sr_txt = self.small_font.render("Rank", True, (255, 255, 255))
        ss_txt = self.small_font.render("Suit", True, (255, 255, 255))
        screen.blit(sr_txt, (self.sort_rank_button.x + 15, self.sort_rank_button.y + 5))
        screen.blit(ss_txt, (self.sort_suit_button.x + 20, self.sort_suit_button.y + 5))

        # deck info bottom right
        deck_rect = pygame.Rect(screen.get_width() - 110, screen.get_height() - 150, 80, 120)
        if self.card_back:
            screen.blit(self.card_back, deck_rect)
        else:
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
                if self.debug:
                    logging.debug("Event: %s", event)
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.play_button and self.play_button.collidepoint(event.pos):
                        self.play_selected_hand()
                    elif self.discard_button and self.discard_button.collidepoint(event.pos):
                        self.discard_selected_cards()
                    elif self.sort_rank_button and self.sort_rank_button.collidepoint(event.pos):
                        self.hand.sort(key=lambda c: RANKS.index(c.rank))
                        self.selected.clear()
                    elif self.sort_suit_button and self.sort_suit_button.collidepoint(event.pos):
                        self.hand.sort(key=lambda c: (SUITS.index(c.suit), RANKS.index(c.rank)))
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
        if self.debug:
            logging.debug("Exiting game loop")
        pygame.quit()

    def replace_selected(self) -> None:
        if not self.selected:
            return
        indices = sorted(self.selected)
        needed = len(indices)
        if self.debug:
            logging.debug("Replacing cards at indices %s", indices)
        if len(self.deck) < needed:
            if self.debug:
                logging.debug("Reshuffling new deck")
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
        if self.debug:
            logging.debug(
                "Played %s for %s chips x%s => %s", name, chips, mult, total
            )
        self.base_chips = chips
        self.multiplier = mult
        self.round_score += total
        self.hands_left -= 1
        self.replace_selected()
        if self.round_score >= self.goal:
            self.round_win()
        elif self.hands_left == 0 and self.round_score < self.goal:
            self.round_loss()

    def discard_selected_cards(self) -> None:
        if not self.selected or self.discards_left <= 0:
            return
        if self.debug:
            logging.debug("Discarding %s cards", len(self.selected))
        self.discards_left -= 1
        self.replace_selected()

    def round_win(self) -> None:
        self.show_message("You win this round!", win=True)
        self.round += 1
        self.goal += 100
        self.round_score = 0
        self.base_chips = 0
        self.multiplier = 0
        self.hands_left = 4
        self.discards_left = 3
        self.deck = Deck()
        self.hand = self.deck.draw(8)
        self.selected.clear()

    def round_loss(self) -> None:
        self.show_message("You're a loser", joker=True)
        self.round = 1
        self.goal = 300
        self.round_score = 0
        self.base_chips = 0
        self.multiplier = 0
        self.hands_left = 4
        self.discards_left = 3
        self.deck = Deck()
        self.hand = self.deck.draw(8)
        self.selected.clear()

    def show_message(self, text: str, win: bool = False, joker: bool = False) -> None:
        if not self.screen:
            return
        clock = pygame.time.Clock()
        particles: List[list] = []
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return
            self.draw_hand()
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            color = [random.randint(100, 255) for _ in range(3)]
            txt = self.font.render(text, True, color)
            rect = txt.get_rect(center=(self.screen.get_width() // 2, 100))
            overlay.blit(txt, rect)
            if win:
                if len(particles) < 100:
                    particles.append([random.randint(0, self.screen.get_width()), 0, random.randint(-2, 2), random.randint(2, 5), [random.randint(0, 255) for _ in range(3)]])
                for p in particles:
                    p[0] += p[2]
                    p[1] += p[3]
                    pygame.draw.circle(overlay, p[4], (int(p[0]), int(p[1])), 3)
            if joker:
                self._draw_joker(overlay)
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            clock.tick(30)

    def _draw_joker(self, surf: pygame.Surface) -> None:
        w, h = surf.get_size()
        cx, cy = w // 2, h // 2
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy + 40), 40)
        pygame.draw.circle(surf, (0, 0, 0), (cx - 15, cy + 30), 5)
        pygame.draw.circle(surf, (0, 0, 0), (cx + 15, cy + 30), 5)
        pygame.draw.arc(surf, (200, 0, 0), (cx - 20, cy + 30, 40, 30), 3.14, 0, 3)


def main(debug: bool = False) -> int:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    game = PokerGame(debug=debug)
    game.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
