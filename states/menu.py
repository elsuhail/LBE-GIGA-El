from __future__ import annotations

from pathlib import Path

import pygame

from config import APP, WHITE
from ui import MUTE_RECT, FontSet, draw_centered_text, draw_mute_button

MENU_BG = (21, 21, 21)

START_POS = (730, 445)
QUIT_POS = (730, 624)
BUTTON_SIZE = (460, 102)
TITLE_Y = 110
BUTTON_FONT_SIZE = 64
BUTTON_TEXT_COLOR = (0, 0, 0)
TEXT_Y_OFFSET = -5


class MenuState:
    def __init__(
        self, screen: pygame.Surface, fonts: FontSet, audio=None
    ) -> None:
        self.screen = screen
        self.fonts = fonts
        self.audio = audio
        base = Path(__file__).parent.parent / "assets" / "UI" / "Main_Menu"
        font_file = Path(__file__).parent.parent / "fonts" / "AmaticSC-Bold.ttf"
        self.button_font = pygame.font.Font(str(font_file), BUTTON_FONT_SIZE)

        def _load(name: str) -> pygame.Surface:
            img = pygame.image.load(str(base / name)).convert_alpha()
            if img.get_size() != BUTTON_SIZE:
                img = pygame.transform.smoothscale(img, BUTTON_SIZE)
            return img

        self.start_img = _load("StartButton.png")
        self.start_hover = _load("StartButtonHover.png")
        self.quit_img = _load("QuitButton.png")
        self.quit_hover = _load("QuitButtonHover.png")
        self.start_rect = pygame.Rect(START_POS, BUTTON_SIZE)
        self.quit_rect = pygame.Rect(QUIT_POS, BUTTON_SIZE)

    def _click(self) -> None:
        # Bunyi klik tombol (diam jika tanpa audio).
        if self.audio is not None:
            self.audio.play_sfx("click")

    def run(self, clock: pygame.time.Clock) -> str:
        # Loop menu. Kembalikan 'start' atau 'quit'.
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if MUTE_RECT.collidepoint(event.pos):
                        if self.audio is not None:
                            self.audio.toggle_mute()
                    elif self.start_rect.collidepoint(event.pos):
                        self._click()
                        return "start"
                    elif self.quit_rect.collidepoint(event.pos):
                        self._click()
                        return "quit"

            self.draw(pygame.mouse.get_pos())
            if self.audio is not None:
                self.audio.update()
            pygame.display.flip()
            clock.tick(APP.fps)

    def draw(self, mouse_pos: tuple[int, int]) -> None:
        # Gambar seluruh layar menu (dipakai run + bisa dites headless).
        self.screen.fill(MENU_BG)
        draw_centered_text(
            self.screen, self.fonts.title, "PUKULIN AJA", APP.width // 2, TITLE_Y, WHITE
        )
        # Pakai mouse_pos parameter agar konsisten (bukan baca mouse 2x).
        start_img = (
            self.start_hover if self.start_rect.collidepoint(mouse_pos) else self.start_img
        )
        quit_img = (
            self.quit_hover if self.quit_rect.collidepoint(mouse_pos) else self.quit_img
        )
        self.screen.blit(start_img, self.start_rect)
        self.screen.blit(quit_img, self.quit_rect)
        for img, rect, text in (
            (start_img, self.start_rect, "START"),
            (quit_img, self.quit_rect, "QUIT"),
        ):
            del img  # sudah di-blit di atas
            img_text = self.button_font.render(text, True, BUTTON_TEXT_COLOR)
            self.screen.blit(
                img_text,
                img_text.get_rect(center=(rect.centerx, rect.centery + TEXT_Y_OFFSET)),
            )
        muted = self.audio.muted if self.audio is not None else False
        draw_mute_button(self.screen, muted, mouse_pos)
