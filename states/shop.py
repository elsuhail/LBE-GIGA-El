"""Layar SHOP: beli kartu, jasa hapus, lanjut stage (layout Figma baru)."""
from __future__ import annotations

from pathlib import Path

import pygame

from config import APP, BALANCE
from game_state import GameState
from ui import MUTE_RECT, FontSet, draw_card, draw_centered_text, draw_mute_button, draw_right_text

SHOP_BG = (21, 21, 21)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY_TEXT = (138, 138, 160)
DARK = (30, 30, 36)
PINK = (255, 79, 163)
PINK_LIGHT = (255, 140, 198)

# Layout browse diukur dari assets/Shop/Shop.png (1920x1080).
TITLE_POS = (89, 55)
SUB_POS = (86, 185)
KOIN_RIGHT = 1837
KOIN_Y = 40
SLOT_Y = 285
SHOP_CARD_W = 213
SHOP_CARD_H = 292
SHOP_CARD_Y = 351
SLOT_X = (85, 443)
BUY_W, BUY_H = 187, 83
BUY_X = (100, 459)
BUY_Y = 662
PANEL_RECT = pygame.Rect(1298, 348, 554, 335)
PANEL_CX = PANEL_RECT.centerx
PRICE_X = 1330
PRICE_Y = 445
COUNT_Y = 490
SELECT_RECT = pygame.Rect(1345, 561, 251, 86)
NEXT_RECT = pygame.Rect(1487, 918, 361, 102)

# Mode hapus (Deck Customization): grid kartu 6x2 di atas panel gelap.
# Diukur dari assets/DeckCust/Deck_Customizatioon.png (1920x1080).
DC_PANEL = pygame.Rect(79, 199, 1762, 684)
DC_PANEL_COLOR = (38, 38, 38)
DC_TITLE_POS = (89, 55)
DC_SUB_POS = (153, 222)
GRID_W, GRID_H = 200, 274
GRID_X0 = 140
GRID_PITCH_X = 286
GRID_Y0 = 284
GRID_PITCH_Y = 299
GRID_COLS = 6
DELETE_RECT = pygame.Rect(79, 917, 381, 106)
BACK_DECK_RECT = pygame.Rect(496, 917, 381, 106)
LEFT_RECT = pygame.Rect(1025, 935, 96, 70)
RIGHT_RECT = pygame.Rect(1229, 935, 96, 70)
PAGE_CX = 1175
PAGE_Y = 952
PAGE_SIZE = 12


def _darken(img: pygame.Surface) -> pygame.Surface:
    """Salinan gelap untuk state disabled (alpha dipertahankan)."""
    out = img.copy()
    out.fill((90, 90, 90, 0), special_flags=pygame.BLEND_RGB_SUB)
    return out


class ShopState:
    """Toko antar stage (mouse only)."""

    def __init__(
        self, screen: pygame.Surface, fonts: FontSet, state: GameState, audio=None
    ) -> None:
        self.screen = screen
        self.fonts = fonts
        self.state = state
        self.audio = audio
        self.mode = "browse"  # atau "remove"
        self.page = 0
        self.selected: int | None = None  # indeks deck yang dipilih
        self.message = ""
        self.buy_enabled = [True, True]
        self.select_enabled = True
        self.confirm_enabled = False

        font_file = str(Path(__file__).parent.parent / "fonts" / "AmaticSC-Bold.ttf")
        self.title_font = pygame.font.Font(font_file, 120)
        self.sub_font = pygame.font.Font(font_file, 40)
        self.slot_font = pygame.font.Font(font_file, 45)
        self.koin_font = pygame.font.Font(font_file, 50)
        self.panel_font = pygame.font.Font(font_file, 64)
        self.info_font = pygame.font.Font(font_file, 32)
        self.buy_font = pygame.font.Font(font_file, 45)
        self.dc_sub_font = pygame.font.Font(font_file, 30)
        self.delete_font = pygame.font.Font(font_file, 44)
        self.page_font = pygame.font.Font(font_file, 30)

        base = Path(__file__).parent.parent / "assets" / "UI" / "Shop"

        def _load(name: str, size: tuple[int, int]) -> pygame.Surface:
            img = pygame.image.load(str(base / name)).convert_alpha()
            if img.get_size() != size:
                img = pygame.transform.smoothscale(img, size)
            return img

        self.buy_img = _load("BuyButton.png", (BUY_W, BUY_H))
        self.buy_hover = _load("BuyButtonHover.png", (BUY_W, BUY_H))
        self.buy_disabled = _darken(self.buy_img)
        self.buy_rects = [pygame.Rect(x, BUY_Y, BUY_W, BUY_H) for x in BUY_X]
        self.panel_img = _load("DeckCust.png", PANEL_RECT.size)
        # Teks Select/Next sudah baked di asset (putih).
        self.select_img = _load("SelectCardGButton.png", SELECT_RECT.size)
        self.select_hover = _load("SelectCardButtonHover.png", SELECT_RECT.size)
        self.select_disabled = _darken(self.select_img)
        self.next_img = _load("NextStageButton.png", NEXT_RECT.size)
        self.next_hover = _load("NextStageButtonHover.png", NEXT_RECT.size)

        deck_base = Path(__file__).parent.parent / "assets" / "UI" / "DeckCust"

        def _load_deck(name: str, size: tuple[int, int]) -> pygame.Surface:
            img = pygame.image.load(str(deck_base / name)).convert_alpha()
            if img.get_size() != size:
                img = pygame.transform.smoothscale(img, size)
            return img

        self.delete_img = _load_deck("DeleteCardButton.png", DELETE_RECT.size)
        self.delete_hover = _load_deck("DeleteCardButtonHover.png", DELETE_RECT.size)
        self.delete_disabled = _darken(self.delete_img)
        self.back_img = _load_deck("BackButtonDeck.png", BACK_DECK_RECT.size)
        self.back_hover = _load_deck("BackButtonDeckHover.png", BACK_DECK_RECT.size)
        self.left_img = _load_deck("LeftPageButton.png", LEFT_RECT.size)
        self.left_hover = _load_deck("LeftPageButtonHover.png", LEFT_RECT.size)
        self.left_disabled = _darken(self.left_img)
        self.right_img = _load_deck("RightPageButton.png", RIGHT_RECT.size)
        self.right_hover = _load_deck("RightPageButtonHover.png", RIGHT_RECT.size)
        self.right_disabled = _darken(self.right_img)

    def enter(self) -> None:
        """Buka shop: generate 2 slot beli, reset mode hapus."""
        self.state.open_shop()
        self.mode = "browse"
        self.page = 0
        self.selected = None
        self.message = (
            f"STAGE {self.state.stage} FINISHED +{self.state.last_reward} COINS"
        )

    def run(self, clock: pygame.time.Clock) -> str:
        """Loop shop. Kembalikan 'encounter' atau 'quit'."""
        self.enter()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.handle_click(event.pos) == "encounter":
                        return "encounter"
            self._refresh()
            self.draw(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
            if self.audio is not None:
                self.audio.update()
            pygame.display.flip()
            clock.tick(APP.fps)

    # ---------- klik ----------

    def _click(self) -> None:
        """Bunyi klik tombol (diam jika tanpa audio)."""
        self._sfx("click")

    def _sfx(self, name: str) -> None:
        """Bunyi SFX apa pun (diam jika tanpa audio)."""
        if self.audio is not None:
            self.audio.play_sfx(name)

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """Tangani klik kiri. Kembalikan 'encounter' jika lanjut stage."""
        if MUTE_RECT.collidepoint(pos):
            if self.audio is not None:
                self.audio.toggle_mute()
            return None
        if NEXT_RECT.collidepoint(pos):
            self._click()
            self.state.next_stage()
            return "encounter"
        if self.mode == "browse":
            for i, rect in enumerate(self.buy_rects):
                if rect.collidepoint(pos):
                    if self.buy_enabled[i]:
                        self._click()
                        ok, info = self.state.buy_shop_card(i)
                        if not ok:
                            self._sfx("error")
                        self.message = (info if ok else f"Gagal: {info}").upper()
                    else:
                        self._sfx("error")
                        sold = (
                            self.state.shop_slots[i] is None
                            if i < len(self.state.shop_slots)
                            else True
                        )
                        self.message = (
                            "SLOT SUDAH TERJUAL" if sold else "GAGAL: KOIN KURANG"
                        )
            if SELECT_RECT.collidepoint(pos):
                if self.select_enabled:
                    self._click()
                    self.mode = "remove"
                    self.page = 0
                    self.selected = None
                    self.message = ""
                else:
                    self._sfx("error")
        else:  # mode remove: pilih kartu / hapus / navigasi / kembali
            for rect, deck_index in self._row_slots():
                if rect.collidepoint(pos):
                    self._click()
                    self.selected = deck_index
            if DELETE_RECT.collidepoint(pos):
                if self.confirm_enabled:
                    ok, info = self.state.remove_deck_card(self.selected or 0)
                    if not ok:
                        self._sfx("error")
                    else:
                        self._sfx("delete")
                    self.message = (info if ok else f"Gagal: {info}").upper()
                    self.selected = None
                else:
                    self._sfx("error")
            if LEFT_RECT.collidepoint(pos):
                if self.page > 0:
                    self._click()
                    self.page -= 1
                    self.selected = None
                else:
                    self._sfx("error")
            max_page = max(0, (len(self.state.master_deck) - 1) // PAGE_SIZE)
            if RIGHT_RECT.collidepoint(pos):
                if self.page < max_page:
                    self._click()
                    self.page += 1
                    self.selected = None
                else:
                    self._sfx("error")
            if BACK_DECK_RECT.collidepoint(pos):
                self._click()
                self.mode = "browse"
                self.selected = None
        return None

    def _refresh(self) -> None:
        """Perbarui status aktif tombol sesuai kondisi kini."""
        for i in range(len(self.buy_rects)):
            sold = self.state.shop_slots[i] is None if i < len(self.state.shop_slots) else True
            self.buy_enabled[i] = (
                not sold and self.state.coins >= BALANCE.shop_card_price
            )
        self.select_enabled = self.state.master_deck.can_use_remove_service()
        self.confirm_enabled = (
            self.selected is not None
            and self.state.master_deck.can_use_remove_service()
            and self.state.coins >= self.state.remove_cost
        )
        max_page = max(0, (len(self.state.master_deck) - 1) // PAGE_SIZE)
        self.page = min(max(self.page, 0), max_page)

    def _row_slots(self) -> list[tuple[pygame.Rect, int]]:
        """Slot kartu deck grid 6x2 di halaman aktif: (rect, indeks deck)."""
        cards = self.state.master_deck.cards
        start = self.page * PAGE_SIZE
        slots: list[tuple[pygame.Rect, int]] = []
        for n, deck_index in enumerate(range(start, min(start + PAGE_SIZE, len(cards)))):
            col, row = n % GRID_COLS, n // GRID_COLS
            rect = pygame.Rect(
                GRID_X0 + col * GRID_PITCH_X,
                GRID_Y0 + row * GRID_PITCH_Y,
                GRID_W,
                GRID_H,
            )
            slots.append((rect, deck_index))
        return slots

    # ---------- gambar ----------

    def _draw_header(self) -> None:
        """Judul + KOIN (judul beda per mode; pesan hanya di browse)."""
        if self.mode == "browse":
            self.screen.blit(self.title_font.render("SHOP", True, WHITE), TITLE_POS)
            if self.message:
                self.screen.blit(
                    self.sub_font.render(self.message, True, WHITE), SUB_POS
                )
        else:
            self.screen.blit(
                self.title_font.render("DECK CUSTOMIZATION", True, WHITE),
                DC_TITLE_POS,
            )
        draw_right_text(
            self.screen,
            self.koin_font,
            f"COINS : {self.state.coins}",
            KOIN_RIGHT,
            KOIN_Y,
        )

    def _draw_image_button(
        self,
        normal: pygame.Surface,
        hover: pygame.Surface,
        disabled: pygame.Surface,
        rect: pygame.Rect,
        enabled: bool,
        mouse_pos: tuple[int, int],
        text: str = "",
        font: pygame.font.Font | None = None,
    ) -> None:
        """Blit tombol image + teks dinamis opsional (mis. BUY)."""
        if not enabled:
            img = disabled
        elif rect.collidepoint(mouse_pos):
            img = hover
        else:
            img = normal
        self.screen.blit(img, rect)
        if text and font is not None:
            img_text = font.render(text, True, BLACK)
            self.screen.blit(
                img_text, img_text.get_rect(center=(rect.centerx, rect.centery - 4))
            )

    def draw(self, mouse_pos: tuple[int, int], mouse_pressed: bool = False) -> None:
        """Gambar seluruh layar shop."""
        del mouse_pressed
        self.screen.fill(SHOP_BG)
        self._draw_header()
        if self.mode == "browse":
            self._draw_browse(mouse_pos)
        else:
            self._draw_remove(mouse_pos)
        self.screen.blit(
            self.next_hover if NEXT_RECT.collidepoint(mouse_pos) else self.next_img,
            NEXT_RECT,
        )
        muted = self.audio.muted if self.audio is not None else False
        draw_mute_button(self.screen, muted, mouse_pos)

    def _draw_browse(self, mouse_pos: tuple[int, int]) -> None:
        """Dua slot beli + panel Deck Customization."""
        from cards import Card as CardObj

        for i, x in enumerate(SLOT_X):
            name = self.state.shop_slots[i] if i < len(self.state.shop_slots) else None
            cx = x + SHOP_CARD_W // 2
            draw_centered_text(self.screen, self.slot_font, f"SLOT {i + 1}", cx, SLOT_Y)
            rect = pygame.Rect(x, SHOP_CARD_Y, SHOP_CARD_W, SHOP_CARD_H)
            if name is None:
                pygame.draw.rect(self.screen, DARK, rect, border_radius=8)
                draw_centered_text(
                    self.screen, self.slot_font, "SOLD", cx,
                    SHOP_CARD_Y + SHOP_CARD_H // 2 - 25, GREY_TEXT,
                )
            else:
                draw_card(self.screen, self.fonts, CardObj(name), rect, True, False)
            self._draw_image_button(
                self.buy_img, self.buy_hover, self.buy_disabled,
                self.buy_rects[i], self.buy_enabled[i], mouse_pos,
                f"BUY ({BALANCE.shop_card_price})", self.buy_font,
            )
        # Panel Deck Customization (teks dinamis di atas panel kosong).
        self.screen.blit(self.panel_img, PANEL_RECT)
        draw_centered_text(
            self.screen, self.panel_font, "DECK CUSTOMIZATION", PANEL_CX, 365, BLACK
        )
        self.screen.blit(
            self.info_font.render(
                f"Price : {self.state.remove_cost} Coins", True, BLACK
            ),
            (PRICE_X, PRICE_Y),
        )
        self.screen.blit(
            self.info_font.render(
                f"Card in Deck : {len(self.state.master_deck)}", True, BLACK
            ),
            (PRICE_X, COUNT_Y),
        )
        if not self.state.master_deck.can_use_remove_service():
            self.screen.blit(
                self.info_font.render(
                    f"Min {BALANCE.min_deck_size} cards to use this", True, BLACK
                ),
                (PRICE_X, COUNT_Y + 38),
            )
        self._draw_image_button(
            self.select_img, self.select_hover, self.select_disabled,
            SELECT_RECT, self.select_enabled, mouse_pos,
        )

    def _draw_remove(self, mouse_pos: tuple[int, int]) -> None:
        """Mode hapus: grid kartu 6x2 + Delete/Back + pagination."""
        pygame.draw.rect(self.screen, DC_PANEL_COLOR, DC_PANEL, border_radius=28)
        sub = self.message if self.message else "SELECT CARD TO REMOVE"
        self.screen.blit(self.dc_sub_font.render(sub, True, WHITE), DC_SUB_POS)
        cards = self.state.master_deck.cards
        for rect, deck_index in self._row_slots():
            card = cards[deck_index]
            draw_card(self.screen, self.fonts, card, rect, True, False)
            if deck_index == self.selected:
                pygame.draw.rect(
                    self.screen, PINK, rect.inflate(8, 8), width=4, border_radius=12
                )
            elif rect.collidepoint(mouse_pos):
                pygame.draw.rect(
                    self.screen, WHITE, rect.inflate(8, 8), width=2, border_radius=12
                )
        total_pages = max(1, (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE)
        max_page = max(0, (len(cards) - 1) // PAGE_SIZE)
        self._draw_image_button(
            self.delete_img, self.delete_hover, self.delete_disabled,
            DELETE_RECT, self.confirm_enabled, mouse_pos,
            f"DELETE CARD ({self.state.remove_cost})", self.delete_font,
        )
        self.screen.blit(
            self.back_hover
            if BACK_DECK_RECT.collidepoint(mouse_pos)
            else self.back_img,
            BACK_DECK_RECT,
        )
        self.screen.blit(
            self.left_disabled
            if self.page <= 0
            else (self.left_hover if LEFT_RECT.collidepoint(mouse_pos) else self.left_img),
            LEFT_RECT,
        )
        self.screen.blit(
            self.right_disabled
            if self.page >= max_page
            else (
                self.right_hover
                if RIGHT_RECT.collidepoint(mouse_pos)
                else self.right_img
            ),
            RIGHT_RECT,
        )
        draw_centered_text(
            self.screen, self.page_font, f"PAGE {self.page + 1}/{total_pages}",
            PAGE_CX, PAGE_Y, WHITE,
        )
