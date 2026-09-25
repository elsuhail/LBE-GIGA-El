"""Helper rendering pygame: font, teks, kartu image, ikon mute.

Seluruh tombol & kartu berupa gambar dari assets/UI; teks dinamis dirender
dengan AmaticSC-Bold.
"""
from __future__ import annotations

import pygame
from dataclasses import dataclass

from config import PINK, WHITE


@dataclass
class FontSet:
    """Kumpulan font Amatic SC berbagai ukuran."""

    small: pygame.font.Font
    medium: pygame.font.Font
    large: pygame.font.Font
    title: pygame.font.Font

    @classmethod
    def default(cls) -> FontSet:
        """Buat FontSet dari AmaticSC-Bold (dipakai semua layar)."""
        from pathlib import Path

        font_path = str(Path(__file__).parent / "fonts" / "AmaticSC-Bold.ttf")
        return cls(
            small=pygame.font.Font(font_path, 30),
            medium=pygame.font.Font(font_path, 42),
            large=pygame.font.Font(font_path, 63),
            title=pygame.font.Font(font_path, 180),
        )


def draw_centered_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    cx: int,
    y: int,
    color: tuple[int, int, int] = WHITE,
) -> None:
    """Gambar teks rata tengah horizontal."""
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(midtop=(cx, y)))


def draw_right_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    right_x: int,
    y: int,
    color: tuple[int, int, int] = WHITE,
) -> None:
    """Gambar teks rata kanan."""
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(topright=(right_x, y)))


CARD_IMAGE_FILES = {
    "Punch": "PunchCard.png",
    "Rest": "RestCard.png",
    "Heavy Smash": "HeavySmashCard.png",
    "Double Strike": "DoubleStrikeCard.png",
    "Adrenaline": "AdrenalineCard.png",
    "Quick Jab": "QuickJabCard.png",
    "Greed": "GreedCard.png",
}

_card_cache: dict[tuple[str, int, int, bool], pygame.Surface] = {}


def get_card_image(name: str, w: int, h: int, playable: bool = True) -> pygame.Surface:
    """Ambil gambar kartu (cache; scale sekali; versi gelap jika tak playable)."""
    key = (name, w, h, playable)
    hit = _card_cache.get(key)
    if hit is not None:
        return hit
    from pathlib import Path

    base = Path(__file__).parent / "assets" / "UI" / "Cards"
    img = pygame.image.load(str(base / CARD_IMAGE_FILES[name])).convert_alpha()
    if img.get_size() != (w, h):
        img = pygame.transform.smoothscale(img, (w, h))
    if not playable:
        img = img.copy()
        img.fill((90, 90, 90, 0), special_flags=pygame.BLEND_RGB_SUB)
    _card_cache[key] = img
    return img


def draw_card(
    surface: pygame.Surface,
    fonts: FontSet,
    card,  # Card (tanpa import sirkular: cukup akses atribut)
    rect: pygame.Rect,
    playable: bool,
    hovered: bool,
) -> None:
    """Blit gambar kartu baru (teks baked; hover = lift oleh caller)."""
    del fonts, hovered
    surface.blit(get_card_image(card.name, rect.w, rect.h, playable), rect)


class FloatingText:
    """Teks melayang naik lalu hilang (mis. '-5' damage di Target)."""

    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int] = PINK,
        ttl: float = 0.9,
        rise: int = 50,
    ) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color
        self.ttl = ttl
        self.rise = rise
        self.age = 0.0

    def update(self, dt: float) -> bool:
        """Majukan umur; kembalikan False jika sudah habis."""
        self.age += dt
        return self.age < self.ttl

    def draw(self, surface: pygame.Surface) -> None:
        """Gambar dengan posisi naik + alpha memudar."""
        progress = min(self.age / self.ttl, 1.0)
        img = self.font.render(self.text, True, self.color)
        img.set_alpha(int(255 * (1.0 - progress)))
        surface.blit(img, img.get_rect(center=(self.x, self.y - self.rise * progress)))


# Ikon mute pojok kanan atas (40x40). Zona kosong di semua layar.
MUTE_RECT = pygame.Rect(1872, 8, 40, 40)
MUTE_GREY = (138, 138, 160)


def draw_mute_button(
    surface: pygame.Surface, muted: bool, mouse_pos: tuple[int, int]
) -> None:
    """Ikon speaker: gelombang pink = bunyi, silang = bisu."""
    rect = MUTE_RECT
    hovered = rect.collidepoint(mouse_pos)
    x, y = rect.x, rect.y
    pygame.draw.rect(surface, (30, 30, 36), rect, border_radius=8)
    pygame.draw.rect(
        surface, PINK if hovered else WHITE, rect, width=2, border_radius=8
    )
    col = MUTE_GREY if muted else WHITE
    pygame.draw.rect(surface, col, (x + 8, y + 15, 7, 10))
    pygame.draw.polygon(
        surface, col, [(x + 15, y + 15), (x + 25, y + 7), (x + 25, y + 33), (x + 15, y + 25)]
    )
    if muted:
        pygame.draw.line(surface, PINK, (x + 27, y + 11), (x + 35, y + 29), 3)
        pygame.draw.line(surface, PINK, (x + 35, y + 11), (x + 27, y + 29), 3)
    else:
        pygame.draw.arc(surface, PINK, (x + 23, y + 13, 10, 14), -1.1, 1.1, 2)
        pygame.draw.arc(surface, PINK, (x + 23, y + 10, 14, 20), -1.0, 1.0, 2)
