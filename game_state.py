from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto

from cards import create_card, shop_pool_names
from config import BALANCE
from deck import CombatPile, MasterDeck


class Phase(Enum):
    # State machine layar (dipakai main.py mulai Fase 2).
    MENU = auto()
    ENCOUNTER = auto()
    SHOP = auto()
    GAME_OVER = auto()


@dataclass
class PlayResult:
    # Hasil sekali main kartu.
    played: bool
    reason: str = ""
    damage: int = 0
    energy_gained: int = 0
    cards_drawn: int = 0
    killed: bool = False
    coins_earned: int = 0
    message: str = ""


class GameState:
    # Satu run: stage, koin, Target, energi, tumpukan kartu, dan Shop.
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng: random.Random = rng if rng is not None else random.Random()
        self.master_deck: MasterDeck = MasterDeck.starter()
        self.pile: CombatPile | None = None
        self.shop_slots: list[str | None] = []
        self.stage: int = 1
        self.best_stage: int = 1  # skor: stage tertinggi yang dicapai
        self.coins: int = BALANCE.starting_coins
        self.last_reward: int = 0  # koin dari kill terakhir (info Shop)
        self.remove_cost: int = BALANCE.remove_base_price
        self.target_name: str = ""
        self.target_hp: int = 0
        self.target_max_hp: int = 0
        self.turn: int = 1
        self.total_turns: int = 0  # akumulasi turn yang dimainkan selama satu run
        self.energy: int = BALANCE.energy_per_turn
        self.stage_cleared: bool = False
        self.run_over: bool = False

    # Run & stage

    def start_run(self) -> None:
        # Mulai run baru dari Stage 1.
        self.master_deck = MasterDeck.starter()
        self.stage = 1
        self.best_stage = 1
        self.coins = BALANCE.starting_coins
        self.last_reward = 0
        self.remove_cost = BALANCE.remove_base_price
        self.total_turns = 0
        self.run_over = False
        self.start_stage()

    def start_stage(self) -> None:
        # Siapkan Target + tumpukan baru, lalu buka Turn 1.
        self.target_max_hp = BALANCE.target_max_hp(self.stage)
        self.target_hp = self.target_max_hp
        self.target_name = BALANCE.target_name(self.stage)
        self.turn = 1
        self.stage_cleared = False
        self.energy = BALANCE.energy_per_turn
        self.pile = CombatPile(self.master_deck.cards, rng=self.rng)
        self.pile.start_stage()
        self.pile.draw_cards(BALANCE.draw_per_turn)
        self.best_stage = max(self.best_stage, self.stage)

    @property
    def hand(self) -> list:
        # Kartu di tangan (list kosong jika pile belum ada).
        if self.pile is None:
            return []
        return self.pile.hand

    @property
    def score(self) -> int:
        # Skor run: stage tertinggi yang dicapai.
        return self.best_stage

    # Main kartu

    def can_play(self, hand_index: int) -> tuple[bool, str]:
        # Cek apakah kartu di tangan bisa dimainkan.
        if self.stage_cleared or self.run_over:
            return False, "stage sudah selesai"
        if self.pile is None:
            return False, "pile belum siap"
        if not 0 <= hand_index < len(self.pile.hand):
            return False, "indeks kartu salah"
        card = self.pile.hand[hand_index]
        if card.cost > self.energy:
            return False, "energi kurang"
        return True, ""

    def play_card(self, hand_index: int) -> PlayResult:
        # Mainkan kartu: bayar energi, terapkan efek, buang ke discard.
        ok, reason = self.can_play(hand_index)
        if not ok or self.pile is None:
            return PlayResult(played=False, reason=reason)
        card = self.pile.take_from_hand(hand_index)
        self.energy -= card.cost  # Guarded by can_play() above.

        damage = card.damage
        if damage:
            self.target_hp = max(0, self.target_hp - damage)

        killed = self.target_hp <= 0
        coins_earned = 0
        energy_gained = 0
        drawn = 0
        if killed:
            # Menang: beri koin (+bonus jika kill via Greed), tempur berakhir.
            self.target_hp = 0
            self.stage_cleared = True
            self.total_turns += 1  # turn saat kill ikut terhitung
            coins_earned = BALANCE.coins_per_kill
            if card.is_greed:
                coins_earned += BALANCE.greed_bonus
            self.coins += coins_earned
            self.last_reward = coins_earned
        else:
            if card.energy_gain:
                self.energy += card.energy_gain
                energy_gained = card.energy_gain
            if card.draw_extra:
                drawn = self.pile.draw_cards(card.draw_extra)

        self.pile.discard_played(card)
        if killed:
            message = f"{card.name} menghancurkan {self.target_name}! +{coins_earned} koin"
        elif damage:
            message = f"{card.name} memberi {damage} damage"
        elif energy_gained:
            message = f"{card.name}: +{energy_gained} energi"
        else:
            message = f"{card.name} dimainkan (tanpa efek)"
        return PlayResult(
            played=True,
            damage=damage,
            energy_gained=energy_gained,
            cards_drawn=drawn,
            killed=killed,
            coins_earned=coins_earned,
            message=message,
        )

    def end_turn(self) -> str:
        if self.stage_cleared:
            return "cleared"
        if self.run_over or self.pile is None:
            return "game_over"
        self.pile.discard_hand()
        if self.turn >= BALANCE.turn_limit:
            self.total_turns += 1  # turn terakhir ikut terhitung
            self.run_over = True
            return "game_over"
        self.total_turns += 1  # satu turn selesai dimainkan
        self.turn += 1
        self.energy = BALANCE.energy_per_turn
        self.pile.draw_cards(BALANCE.draw_per_turn)
        return "next_turn"

    # Shop

    def open_shop(self) -> list[str | None]:
        # Generate 2 slot beli (kartu acak berbeda). Hanya setelah menang.
        if not self.stage_cleared:
            raise RuntimeError("Shop hanya dibuka setelah Target hancur")
        self.shop_slots = self.rng.sample(shop_pool_names(), k=2)
        return list(self.shop_slots)

    def buy_shop_card(self, slot: int) -> tuple[bool, str]:
        # Beli kartu di slot; slot terisi jadi kosong.
        if not self.stage_cleared:
            return False, "belum menang"
        if not 0 <= slot < len(self.shop_slots):
            return False, "slot salah"
        name = self.shop_slots[slot]
        if name is None:
            return False, "slot kosong"
        if self.coins < BALANCE.shop_card_price:
            return False, "koin kurang"
        self.coins -= BALANCE.shop_card_price
        self.master_deck.add(create_card(name))
        self.shop_slots[slot] = None
        return True, f"membeli {name}"

    def remove_deck_card(self, deck_index: int) -> tuple[bool, str]:
        # Buang permanen 1 kartu dari deck; harga naik tiap dipakai.
        if not self.stage_cleared:
            return False, "belum menang"
        if not self.master_deck.can_use_remove_service():
            return False, f"deck minimal {BALANCE.min_deck_size} kartu"
        if not 0 <= deck_index < len(self.master_deck):
            return False, "indeks deck salah"
        if self.coins < self.remove_cost:
            return False, "koin kurang"
        removed = self.master_deck.remove_at(deck_index)
        self.coins -= self.remove_cost
        self.remove_cost += BALANCE.remove_price_step
        return True, f"membuang {removed.name}"

    def next_stage(self) -> None:
        # Lanjut ke stage berikutnya (hanya setelah menang).
        if not self.stage_cleared:
            raise RuntimeError("Next stage hanya setelah Target hancur")
        self.stage += 1
        self.start_stage()
