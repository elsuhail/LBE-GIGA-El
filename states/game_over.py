from __future__ import annotations

from pathlib import Path

import pygame

from game_state import GameState
from ui import MUTE_RECT, FontSet, draw_centered_text, draw_mute_button, draw_right_text

GO_BG = (0, 0, 0)
GO_PINK = (237, 0, 142)
GO_DIVIDER = (248, 160, 213)
GO_BLACK = (0, 0, 0)
GO_GREY = (105, 105, 105)
GO_BOX_FILL = (253, 229, 243)
GO_WHITE = (255, 255, 255)
GO_PILL = (21, 21, 21)

PANEL_RECT = pygame.Rect(520, 170, 877, 765)
PANEL_CX = PANEL_RECT.centerx
TITLE_Y = 220
SUB_Y = 348
STATS_RECT = pygame.Rect(560, 443, 793, 214)
LABEL_X = 620
LABEL_Y = 467
VALUE_RIGHT = 1325
VALUE_Y = 454
DIVIDER_Y = 530
COL2_X = 850
ROW2_LABEL_Y = 548
ROW2_VALUE_Y = 586
PILL_RECT = pygame.Rect(1154, 566, 148, 46)
TRY_RECT = pygame.Rect(780, 695, 367, 87)
LINK_RECT = pygame.Rect(826, 801, 266, 69)


class GameOverState:
    def __init__(
        self, screen: pygame.Surface, fonts: FontSet, state: GameState, audio=None
    ) -> None:
        self.screen = screen
        self.fonts = fonts
        self.state = state
        self.audio = audio

        font_file = str(Path(__file__).parent.parent / "fonts" / "AmaticSC-Bold.ttf")
        self.title_font = pygame.font.Font(font_file, 110)
        self.sub_font = pygame.font.Font(font_file, 47)
        self.label_font = pygame.font.Font(font_file, 32)
        self.value_font = pygame.font.Font(font_file, 58)
        self.small_font = pygame.font.Font(font_file, 28)
        self.big_font = pygame.font.Font(font_file, 36)
        self.pill_font = pygame.font.Font(font_file, 24)

        base = Path(__file__).parent.parent / "assets" / "UI" / "Ending"

        def _load(name: str, size: tuple[int, int]) -> pygame.Surface:
            img = pygame.image.load(str(base / name)).convert_alpha()
            if img.get_size() != size:
                img = pygame.transform.smoothscale(img, size)
            return img

        self.panel_img = _load("PanelGameOver.png", PANEL_RECT.size)
        # Teks Try Again baked di asset (hitam normal, putih hover).
        self.try_img = _load("TRY AGAIN Button.png", TRY_RECT.size)
        self.try_hover = _load("TRY AGAIN Hover.png", TRY_RECT.size)
        # Link: hitam normal, pink saat hover (lihat referensi = state hover).
        self.link_img = _load("Back to Menu Wrapper.png", LINK_RECT.size)
        self.link_hover = _load("Back to Menu Hover.png", LINK_RECT.size)

    def run(self, clock: pygame.time.Clock) -> str:
        # Loop game over. Kembalikan 'restart', 'menu', atau 'quit'.
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self.handle_click(event.pos)
                    if result is not None:
                        return result
            self.draw(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
            if self.audio is not None:
                self.audio.update()
            pygame.display.flip()
            clock.tick(60)

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        # Tangani klik kiri. Kembalikan 'restart'/'menu' atau None.
        if MUTE_RECT.collidepoint(pos):
            if self.audio is not None:
                self.audio.toggle_mute()
            return None
        if TRY_RECT.collidepoint(pos):
            self._click()
            return "restart"
        if LINK_RECT.collidepoint(pos):
            self._click()
            return "menu"
        return None

    def _click(self) -> None:
        # Bunyi klik tombol (diam jika tanpa audio).
        if self.audio is not None:
            self.audio.play_sfx("click")

    def _draw_glow(self) -> None:
        # Rona magenta samar di belakang panel (lihat referensi).
        glow = pygame.Surface((1000, 700), pygame.SRCALPHA)
        for radius, alpha in ((480, 8), (340, 10), (200, 12)):
            pygame.draw.circle(
                glow, (120, 20, 60, alpha), (500, 300), radius
            )
        self.screen.blit(glow, (460, 0))

    def draw(self, mouse_pos: tuple[int, int], mouse_pressed: bool = False) -> None:
        # Gambar panel skor + tombol.
        del mouse_pressed
        state = self.state
        self.screen.fill(GO_BG)
        self._draw_glow()
        self.screen.blit(self.panel_img, PANEL_RECT)

        draw_centered_text(
            self.screen, self.title_font, "GAME OVER", PANEL_CX, TITLE_Y, GO_PINK
        )
        draw_centered_text(
            self.screen,
            self.sub_font,
            "YOU GOT KNOCKED OUT!",
            PANEL_CX,
            SUB_Y,
            GO_BLACK,
        )

        # Kotak stats: fill pink muda + border pink.
        pygame.draw.rect(self.screen, GO_BOX_FILL, STATS_RECT, border_radius=20)
        pygame.draw.rect(
            self.screen, GO_PINK, STATS_RECT, width=2, border_radius=20
        )
        self.screen.blit(
            self.label_font.render("STAGE REACHED", True, GO_BLACK),
            (LABEL_X, LABEL_Y),
        )
        draw_right_text(
            self.screen,
            self.value_font,
            f"STAGE {state.stage} ({state.target_name})".upper(),
            VALUE_RIGHT,
            VALUE_Y,
            GO_PINK,
        )
        pygame.draw.line(
            self.screen, GO_DIVIDER, (LABEL_X, DIVIDER_Y), (VALUE_RIGHT, DIVIDER_Y), 2
        )
        self.screen.blit(
            self.small_font.render("COINS COLLECTED", True, GO_GREY),
            (LABEL_X, ROW2_LABEL_Y),
        )
        self.screen.blit(
            self.big_font.render(f"{state.coins} COINS", True, GO_BLACK),
            (LABEL_X, ROW2_VALUE_Y),
        )
        self.screen.blit(
            self.small_font.render("TOTAL TURNS", True, GO_GREY),
            (COL2_X, ROW2_LABEL_Y),
        )
        self.screen.blit(
            self.big_font.render(f"{state.total_turns} TURNS", True, GO_BLACK),
            (COL2_X, ROW2_VALUE_Y),
        )
        pygame.draw.rect(self.screen, GO_PILL, PILL_RECT, border_radius=23)
        img = self.pill_font.render(
            f"{len(state.master_deck)} CARDS IN DECK", True, GO_WHITE
        )
        self.screen.blit(img, img.get_rect(center=PILL_RECT.center))

        self.screen.blit(
            self.try_hover if TRY_RECT.collidepoint(mouse_pos) else self.try_img,
            TRY_RECT,
        )
        self.screen.blit(
            self.link_hover if LINK_RECT.collidepoint(mouse_pos) else self.link_img,
            LINK_RECT,
        )
        muted = self.audio.muted if self.audio is not None else False
        draw_mute_button(self.screen, muted, mouse_pos)
