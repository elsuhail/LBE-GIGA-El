"""Manajemen audio: BGM per fase + SFX (jadwal tunda + ducking).

Gagal aman: file hilang / device audio tak ada -> game tetap jalan bisu.
"""
from __future__ import annotations

from pathlib import Path

import pygame

BGM_VOLUME = 0.5
SFX_VOLUME = 0.7
DUCK_VOLUME = 0.12  # volume BGM saat fanfare kill main
KILL_DUCK_MS = 4200  # kill 3.7s + coin susulan
COIN_DELAY_MS = 400  # coin masuk sesaat setelah kill, tidak menumpuk

BGM_FILES = {
    "menu": "bgm_menu.ogg",
    "encounter": "bgm_encounter.ogg",
    "shop": "bgm_shop.ogg",
    "gameover": "bgm_gameOver.ogg",
}

SFX_FILES = {
    "click": "sfx_click.wav",
    "cardplay": "sfx_cardPlay.wav",
    "hit": "sfx_hit.wav",
    "kill": "sfx_kill.wav",
    "coin": "sfx_coin.wav",
    "error": "sfx_error.wav",
    "delete": "sfx_deleteCard.wav",
}


class AudioManager:
    """Pemutar BGM. Panggil play_bgm() tiap ganti fase (no-op jika sama)."""

    def __init__(
        self,
        base_dir: str | Path | None = None,
        bgm_volume: float = BGM_VOLUME,
        sfx_volume: float = SFX_VOLUME,
    ) -> None:
        self.base = (
            Path(base_dir)
            if base_dir is not None
            else Path(__file__).parent / "assets" / "audio" / "bgm"
        )
        self.sfx_base = Path(__file__).parent / "assets" / "audio" / "sfx"
        self.bgm_volume = bgm_volume
        self.sfx_volume = sfx_volume
        self.current: str | None = None
        self.muted: bool = False
        self._sfx: dict[str, pygame.mixer.Sound] = {}
        self._pending: list[tuple[int, str]] = []  # (tenggat ticks, nama SFX)
        self._duck_until: int = 0
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def play_bgm(self, name: str, fade_ms: int = 600) -> None:
        """Putar BGM loop. Ganti hanya jika beda dari yang sedang main."""
        if not self.enabled or name == self.current or name not in BGM_FILES:
            return
        path = self.base / BGM_FILES[name]
        if not path.is_file():
            return
        try:
            pygame.mixer.music.load(str(path))
            # Hormati duck yang sedang aktif (mis. fanfare kill ke Shop).
            pygame.mixer.music.set_volume(self._music_level())
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self.current = name
        except pygame.error:
            return

    def _music_level(self) -> float:
        """Volume musik saat ini (0 jika mute, turun jika duck aktif)."""
        if self.muted:
            return 0.0
        if self._duck_until > pygame.time.get_ticks():
            return DUCK_VOLUME
        return self.bgm_volume

    def toggle_mute(self) -> bool:
        """Bisu / bunyi lagi. Kembalikan status muted."""
        if not self.enabled:
            return self.muted
        self.muted = not self.muted
        try:
            pygame.mixer.music.set_volume(self._music_level())
            for sound in self._sfx.values():
                sound.set_volume(0.0 if self.muted else self.sfx_volume)
        except pygame.error:
            pass
        return self.muted

    def stop_bgm(self, fade_ms: int = 400) -> None:
        """Hentikan BGM (fade out)."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except pygame.error:
            pass
        self.current = None

    def play_sfx(self, name: str) -> None:
        """Putar SFX sekali (lazy-load + cache)."""
        if not self.enabled or self.muted or name not in SFX_FILES:
            return
        sound = self._sfx.get(name)
        if sound is None:
            path = self.sfx_base / SFX_FILES[name]
            if not path.is_file():
                return
            try:
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(self.sfx_volume)
                self._sfx[name] = sound
            except pygame.error:
                return
        try:
            sound.play()
        except pygame.error:
            pass

    def schedule_sfx(self, name: str, delay_ms: int = 0) -> None:
        """Jadwalkan SFX main N ms lagi (diproses di update())."""
        if not self.enabled or name not in SFX_FILES:
            return
        self._pending.append((pygame.time.get_ticks() + delay_ms, name))

    def duck(self, duration_ms: int, level: float = DUCK_VOLUME) -> None:
        """Turunkan BGM sementara agar fanfare/SFX panjang terdengar jelas."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.set_volume(level)
        except pygame.error:
            return
        self._duck_until = pygame.time.get_ticks() + duration_ms

    def update(self) -> None:
        """Panggil tiap frame: mainkan SFX jatuh tempo + pulihkan volume."""
        if not self.enabled:
            return
        now = pygame.time.get_ticks()
        due = [p for p in self._pending if p[0] <= now]
        self._pending = [p for p in self._pending if p[0] > now]
        for _, name in due:
            self.play_sfx(name)
        if self._duck_until and now >= self._duck_until:
            self._duck_until = 0
            try:
                pygame.mixer.music.set_volume(self._music_level())
            except pygame.error:
                pass
