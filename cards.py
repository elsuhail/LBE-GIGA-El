"""Definisi kartu sebagai objek data (tanpa aturan tempur).

Aturan tempur (damage, energi, draw) ada di game_state.py.
"""
from __future__ import annotations

from config import BALANCE


class Card:
    """Satu kartu fisik di deck / tangan. Stat diambil dari config."""

    __slots__ = ("name", "cost", "damage", "energy_gain", "draw_extra", "is_greed", "text")

    def __init__(self, name: str) -> None:
        try:
            spec = BALANCE.card_specs[name]
        except KeyError:
            raise ValueError(f"Kartu tidak dikenal: {name!r}") from None
        self.name: str = name
        self.cost: int = spec.cost
        self.damage: int = spec.damage
        self.energy_gain: int = spec.energy_gain
        self.draw_extra: int = spec.draw_extra
        self.is_greed: bool = spec.greed
        self.text: str = spec.text

    @property
    def description(self) -> str:
        """Teks efek untuk ditampilkan di kartu."""
        return self.text

    def clone(self) -> Card:
        """Salinan kartu baru dengan nama sama."""
        return Card(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Card({self.name!r})"


def create_card(name: str) -> Card:
    """Factory satu kartu berdasarkan nama."""
    return Card(name)


def create_starter_deck() -> list[Card]:
    """Starter deck: Punch x6 + Rest x4 (isi dari config)."""
    cards: list[Card] = []
    for name, count in BALANCE.starter_deck.items():
        cards.extend(Card(name) for _ in range(count))
    return cards


def shop_pool_names() -> list[str]:
    """Nama-nama kartu yang bisa muncul di Shop."""
    return list(BALANCE.shop_pool)
