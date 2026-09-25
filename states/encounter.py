"""Layar ENCOUNTER: pertarungan kartu melawan Target statis (layout Figma baru)."""
from __future__ import annotations

from pathlib import Path

import pygame

from audio import COIN_DELAY_MS, KILL_DUCK_MS
from config import APP, BALANCE, WHITE
from game_state import GameState
from ui import (
    MUTE_RECT,
    FloatingText,
    FontSet,
    draw_card,
    draw_centered_text,
    draw_mute_button,
    draw_right_text,
)

# Kartu image baru 213x292; pitch 283 + center 748 diukur dari referensi.
CARD_W = 213
CARD_H = 292
CARD_PITCH = 283
ROW_CX = 748
MAX_ROW_W = 1360
CARDS_Y = 726
HOVER_LIFT = 10
FLOAT_Y = 285  # di bawah teks HP (HP 217-246 di referensi)

# Layout diukur dari assets/Encounter/Encounter.png (1920x1080).
ENCOUNTER_BG = (21, 21, 21)
HP_EMPTY = (30, 30, 36)
HP_BAR_RECT = pygame.Rect(711, 133, 492, 67)
HP_TEXT_Y = 212
STAGE_POS = (82, 40)
ENEMY_Y = 30
ENERGY_POS = (1856, 28)  # right_x, y
KOIN_POS = (1856, 95)
TURN_POS = (93, 620)
DRAW_POS = (1487, 710)
DISCARD_POS = (1487, 770)
MESSAGE_Y = 640
END_RECT = pygame.Rect(1487, 918, 361, 102)


class EncounterState:
    """Satu encounter. Menang -> 'shop', kalah -> 'game_over'."""

    def __init__(
        self, screen: pygame.Surface, fonts: FontSet, state: GameState, audio=None
    ) -> None:
        self.screen = screen
        self.fonts = fonts
        self.state = state
        self.audio = audio
        self.message = ""
        self.floaters: list[FloatingText] = []
        self._spawn_count = 0

        font_file = str(Path(__file__).parent.parent / "fonts" / "AmaticSC-Bold.ttf")
        self.stage_font = pygame.font.Font(font_file, 100)
        self.enemy_font = pygame.font.Font(font_file, 80)
        self.hp_font = pygame.font.Font(font_file, 40)
        self.hud_font = pygame.font.Font(font_file, 50)

        base = Path(__file__).parent.parent / "assets" / "UI" / "Encounter"
        self.end_img = pygame.image.load(str(base / "EndTurnButton.png")).convert_alpha()
        self.end_hover = pygame.image.load(
            str(base / "EndTurnButtonHover.png")
        ).convert_alpha()
        if self.end_img.get_size() != END_RECT.size:
            self.end_img = pygame.transform.smoothscale(self.end_img, END_RECT.size)
            self.end_hover = pygame.transform.smoothscale(self.end_hover, END_RECT.size)
        self.hp_img = pygame.image.load(str(base / "HealthBar.png")).convert_alpha()
        if self.hp_img.get_size() != HP_BAR_RECT.size:
            self.hp_img = pygame.transform.smoothscale(self.hp_img, HP_BAR_RECT.size)

    def run(self, clock: pygame.time.Clock) -> str:
        """Loop encounter. Kembalikan 'shop', 'game_over', atau 'quit'."""
        self.message = self._stage_intro()
        self.floaters = []
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self.handle_click(event.pos)
                    if result is not None:
                        return result
            dt = clock.tick(APP.fps) / 1000.0
            self.floaters = [f for f in self.floaters if f.update(dt)]
            self.draw(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
            if self.audio is not None:
                self.audio.update()
            pygame.display.flip()

    # ---------- klik ----------

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """Tangani klik kiri. Kembalikan 'shop'/'game_over' atau None."""
        if MUTE_RECT.collidepoint(pos):
            if self.audio is not None:
                self.audio.toggle_mute()
            return None
        if self.state.stage_cleared:
            return "shop"
        if self.state.run_over:
            return "game_over"
        if END_RECT.collidepoint(pos):
            self._click()
            result = self.state.end_turn()
            if result == "game_over":
                return "game_over"
            # Info turn sudah ada di HUD kiri; pesan dikosongkan agar tak ganda.
            self.message = ""
            return None
        rects = self._card_rects(pos)
        for i in reversed(range(len(rects))):
            rect = rects[i]
            if rect.collidepoint(pos):
                play = self.state.play_card(i)
                self.message = play.message if play.played else f"Tidak bisa: {play.reason}"
                if play.played:
                    self._sfx("cardplay")
                else:
                    self._sfx("error")
                    return None
                if play.damage > 0:
                    self._spawn_damage(play.damage)
                    self._sfx("hit")
                if play.killed:
                    self._sfx("kill")
                    if self.audio is not None:
                        # BGM ditundukkan + coin susulan agar tak menumpuk.
                        self.audio.duck(KILL_DUCK_MS)
                        if play.coins_earned > 0:
                            self.audio.schedule_sfx("coin", COIN_DELAY_MS)
                    elif play.coins_earned > 0:
                        self._sfx("coin")
                    return "shop"
                return None
        return None

    def _click(self) -> None:
        """Bunyi klik tombol (diam jika tanpa audio)."""
        self._sfx("click")

    def _sfx(self, name: str) -> None:
        """Bunyi SFX apa pun (diam jika tanpa audio)."""
        if self.audio is not None:
            self.audio.play_sfx(name)

    def _spawn_damage(self, damage: int) -> None:
        """Angka '-N' melayang di bawah HP bar."""
        self._spawn_count += 1
        x = APP.width // 2 + ((self._spawn_count * 71) % 180) - 90
        self.floaters.append(FloatingText(x, FLOAT_Y, f"-{damage}", self.hud_font))

    def _stage_intro(self) -> str:
        """Pesan pembuka tiap stage."""
        return f"Stage {self.state.stage}: kalahkan {self.state.target_name}!"

    # ---------- gambar ----------

    def _is_playable(self, index: int) -> bool:
        """Kartu bisa dimainkan jika energi cukup dan stage belum selesai."""
        card = self.state.hand[index]
        return card.cost <= self.state.energy and not self.state.stage_cleared

    def _card_rects(self, mouse_pos: tuple[int, int] | None = None) -> list[pygame.Rect]:
        """Rect kartu tangan; pitch menciut jika tangan penuh; hover naik."""
        n = len(self.state.hand)
        if n == 0:
            return []
        pitch = CARD_PITCH
        if n > 1:
            pitch = min(CARD_PITCH, (MAX_ROW_W - CARD_W) // (n - 1))
        total = (n - 1) * pitch + CARD_W
        start_x = ROW_CX - total // 2
        rects = [
            pygame.Rect(start_x + i * pitch, CARDS_Y, CARD_W, CARD_H)
            for i in range(n)
        ]
        if mouse_pos is not None:
            for i in reversed(range(n)):
                if rects[i].collidepoint(mouse_pos) and self._is_playable(i):
                    rects[i] = rects[i].move(0, -HOVER_LIFT)
                    break
        return rects

    def _draw_hp_bar(self) -> None:
        """HP bar image: HealthBar.png di-clip sesuai HP, sisa gelap."""
        state = self.state
        ratio = (state.target_hp / state.target_max_hp) if state.target_max_hp > 0 else 0
        fill_w = int(HP_BAR_RECT.w * max(0.0, min(1.0, ratio)))
        if fill_w > 0:
            # Clip kiri agar cap kiri + tekstur jagged tidak penyok (tidak di-scale).
            fill = self.hp_img.subsurface(pygame.Rect(0, 0, fill_w, HP_BAR_RECT.h))
            self.screen.blit(fill, HP_BAR_RECT.topleft)
        if fill_w < HP_BAR_RECT.w:
            # Track gelap hanya untuk sisa yang kosong (asset transparan di
            # ceruk jagged akan menembus ke BG, bukan ke track).
            empty = pygame.Rect(
                HP_BAR_RECT.x + fill_w, HP_BAR_RECT.y,
                HP_BAR_RECT.w - fill_w, HP_BAR_RECT.h,
            )
            pygame.draw.rect(self.screen, HP_EMPTY, empty)

    def draw(self, mouse_pos: tuple[int, int], mouse_pressed: bool = False) -> None:
        """Gambar seluruh layar encounter sesuai referensi Figma."""
        state = self.state
        self.screen.fill(ENCOUNTER_BG)

        # Kiri atas: STAGE (100). Tengah: nama musuh (80).
        self.screen.blit(
            self.stage_font.render(f"STAGE {state.stage}", True, WHITE), STAGE_POS
        )
        draw_centered_text(
            self.screen, self.enemy_font, state.target_name, APP.width // 2, ENEMY_Y
        )

        # HP bar image + angka HP di bawahnya (40).
        self._draw_hp_bar()
        draw_centered_text(
            self.screen,
            self.hp_font,
            f"{state.target_hp}/{state.target_max_hp}",
            HP_BAR_RECT.centerx,
            HP_TEXT_Y,
            WHITE,
        )

        # Kanan atas: ENERGY + KOIN (50, rata kanan).
        draw_right_text(
            self.screen, self.hud_font, f"ENERGY : {state.energy}", *ENERGY_POS
        )
        draw_right_text(
            self.screen, self.hud_font, f"COINS : {state.coins}", *KOIN_POS
        )

        # Kiri tengah: TURN.
        self.screen.blit(
            self.hud_font.render(
                f"TURN : {state.turn}/{BALANCE.turn_limit}", True, WHITE
            ),
            TURN_POS,
        )

        # Pesan aksi (40) + tangan + End Turn image.
        if self.message:
            draw_centered_text(
                self.screen, self.hp_font, self.message, APP.width // 2, MESSAGE_Y
            )
        for i, rect in enumerate(self._card_rects(mouse_pos)):
            playable = self._is_playable(i)
            draw_card(
                self.screen, self.fonts, state.hand[i], rect, playable,
                rect.collidepoint(mouse_pos),
            )
        # DRAW / DISCARD di atas kartu (sesuai layer Figma) agar tak tertutup.
        draw_count = state.pile.draw_count if state.pile is not None else 0
        discard_count = state.pile.discard_count if state.pile is not None else 0
        self.screen.blit(
            self.hud_font.render(f"DRAW : {draw_count}", True, WHITE), DRAW_POS
        )
        self.screen.blit(
            self.hud_font.render(f"DISCARD : {discard_count}", True, WHITE),
            DISCARD_POS,
        )
        self.screen.blit(
            self.end_hover if END_RECT.collidepoint(mouse_pos) else self.end_img,
            END_RECT,
        )
        for floater in self.floaters:
            floater.draw(self.screen)
        muted = self.audio.muted if self.audio is not None else False
        draw_mute_button(self.screen, muted, mouse_pos)
