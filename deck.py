"""Manajemen tumpukan kartu: draw pile, tangan, discard pile.

Dua class:
- MasterDeck: koleksi permanen pemain (persisten antar stage, diubah via Shop).
- CombatPile: tumpukan tempur satu stage (draw / hand / discard + reshuffle).
"""
from __future__ import annotations

import random
from collections.abc import Iterable

from cards import Card, create_starter_deck
from config import BALANCE


class MasterDeck:
    """Deck permanen milik pemain."""

    def __init__(self, cards: Iterable[Card] | None = None) -> None:
        self._cards: list[Card] = list(cards) if cards is not None else []

    @classmethod
    def starter(cls) -> MasterDeck:
        """MasterDeck berisi starter deck dari config."""
        return cls(create_starter_deck())

    @property
    def cards(self) -> list[Card]:
        """Salinan daftar kartu (biar tidak dimutasi dari luar)."""
        return list(self._cards)

    def __len__(self) -> int:
        return len(self._cards)

    def size(self) -> int:
        """Jumlah kartu di deck."""
        return len(self._cards)

    def add(self, card: Card) -> None:
        """Kartu beli masuk ke deck."""
        self._cards.append(card)

    def remove_at(self, index: int) -> Card:
        """Buang permanen kartu pada indeks; error jika indeks salah."""
        return self._cards.pop(index)

    def can_use_remove_service(self) -> bool:
        """Jasa hapus terkunci jika deck <= batas minimal."""
        return len(self._cards) > BALANCE.min_deck_size

    def count_by_name(self) -> dict[str, int]:
        """Ringkasan isi deck: nama -> jumlah."""
        counts: dict[str, int] = {}
        for card in self._cards:
            counts[card.name] = counts.get(card.name, 0) + 1
        return counts


class CombatPile:
    """Tumpukan tempur: draw pile, tangan, discard pile + reshuffle."""

    def __init__(
        self,
        cards: Iterable[Card],
        rng: random.Random | None = None,
        max_hand: int = BALANCE.max_hand,
    ) -> None:
        self._rng: random.Random = rng if rng is not None else random.Random()
        self.max_hand: int = max_hand
        self.draw_pile: list[Card] = list(cards)
        self.hand: list[Card] = []
        self.discard_pile: list[Card] = []

    def start_stage(self) -> None:
        """Kumpulkan semua kartu lalu kocok jadi draw pile baru."""
        gathered = self.draw_pile + self.hand + self.discard_pile
        self._rng.shuffle(gathered)
        self.draw_pile = gathered
        self.hand = []
        self.discard_pile = []

    def _reshuffle_if_needed(self) -> None:
        """Jika draw habis, kocok discard jadi draw baru."""
        if not self.draw_pile and self.discard_pile:
            self.draw_pile = self.discard_pile
            self.discard_pile = []
            self._rng.shuffle(self.draw_pile)

    def draw_cards(self, count: int) -> int:
        """Tarik kartu ke tangan (patuhi reshuffle + batas tangan)."""
        drawn = 0
        for _ in range(count):
            if len(self.hand) >= self.max_hand:
                break
            self._reshuffle_if_needed()
            if not self.draw_pile:  # draw + discard sama-sama kosong
                break
            self.hand.append(self.draw_pile.pop())
            drawn += 1
        return drawn

    def take_from_hand(self, index: int) -> Card:
        """Ambil kartu dari tangan untuk dimainkan."""
        return self.hand.pop(index)

    def discard_played(self, card: Card) -> None:
        """Kartu yang dimainkan masuk discard pile."""
        self.discard_pile.append(card)

    def discard_hand(self) -> None:
        """Sisa tangan (End Turn) masuk discard pile."""
        self.discard_pile.extend(self.hand)
        self.hand.clear()

    @property
    def draw_count(self) -> int:
        """Jumlah kartu di draw pile."""
        return len(self.draw_pile)

    @property
    def discard_count(self) -> int:
        """Jumlah kartu di discard pile."""
        return len(self.discard_pile)

    @property
    def total_count(self) -> int:
        """Total kartu di semua tumpukan tempur."""
        return len(self.draw_pile) + len(self.hand) + len(self.discard_pile)
