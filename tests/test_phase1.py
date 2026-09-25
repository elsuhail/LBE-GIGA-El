"""Tes logika headless (tanpa UI/pygame). Jalankan: python -m tests.test_phase1."""
from __future__ import annotations

import random
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cards import Card, create_starter_deck
from config import BALANCE
from deck import CombatPile, MasterDeck
from game_state import GameState

PASS = 0
FAIL = 0


def check(name: str, cond: bool) -> None:
    """Catat hasil satu asersi."""
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {name}")
    else:
        FAIL += 1
        print(f"  [GAGAL] {name}")


def fresh_state(seed: int = 0) -> GameState:
    """GameState baru yang sudah start_run (deterministik)."""
    state = GameState(rng=random.Random(seed))
    state.start_run()
    return state


def test_starter_deck() -> None:
    print("== starter deck ==")
    cards = create_starter_deck()
    check("isi 10 kartu", len(cards) == 10)
    names = [c.name for c in cards]
    check("Punch x6", names.count("Punch") == 6)
    check("Rest x4", names.count("Rest") == 4)


def test_hp_scaling() -> None:
    print("== HP scaling ==")
    check("stage 1 = 30", BALANCE.target_max_hp(1) == 30)
    check("stage 2 = 45", BALANCE.target_max_hp(2) == 45)
    check("stage 3 = 60", BALANCE.target_max_hp(3) == 60)
    check("nama stage 1 Tralalelo Tralala", BALANCE.target_name(1) == "Tralalelo Tralala")
    check("nama stage 2 Bombini Gusini", BALANCE.target_name(2) == "Bombini Gusini")


def test_start_stage() -> None:
    print("== awal stage ==")
    state = fresh_state()
    check("HP 30/30", state.target_hp == 30 and state.target_max_hp == 30)
    check("turn 1/3", state.turn == 1)
    check("energi 3", state.energy == 3)
    check("tangan 5 kartu", len(state.hand) == 5)
    assert state.pile is not None
    check("total kartu tetap 10", state.pile.total_count == 10)


def test_play_punch() -> None:
    print("== main Punch ==")
    state = fresh_state()
    assert state.pile is not None
    state.pile.hand = [Card("Punch")]
    state.energy = 3
    res = state.play_card(0)
    check("berhasil dimainkan", res.played)
    check("damage 5, HP 25", state.target_hp == 25)
    check("energi 3->2", state.energy == 2)
    check("kartu masuk discard", state.pile.discard_count == 1)


def test_insufficient_energy() -> None:
    print("== energi kurang ==")
    state = fresh_state()
    assert state.pile is not None
    state.pile.hand = [Card("Heavy Smash")]
    state.energy = 2
    res = state.play_card(0)
    check("ditolak", not res.played)
    check("kartu tetap di tangan", len(state.hand) == 1)
    check("energi tidak berkurang", state.energy == 2)


def test_rest_no_effect() -> None:
    print("== Rest ==")
    state = fresh_state()
    assert state.pile is not None
    state.pile.hand = [Card("Rest")]
    state.energy = 0
    res = state.play_card(0)
    check("cost 0 tetap bisa", res.played)
    check("HP tetap", state.target_hp == 30)
    check("masuk discard", state.pile.discard_count == 1)


def test_adrenaline() -> None:
    print("== Adrenaline ==")
    state = fresh_state()
    assert state.pile is not None
    state.pile.hand = [Card("Adrenaline")]
    state.energy = 1
    res = state.play_card(0)
    check("berhasil", res.played)
    check("energi 1->3", state.energy == 3 and res.energy_gained == 2)


def test_quick_jab_draw() -> None:
    print("== Quick Jab ==")
    state = fresh_state()
    assert state.pile is not None
    state.pile.hand = [Card("Quick Jab")]
    state.pile.draw_pile = [Card("Punch"), Card("Rest")]
    state.pile.discard_pile = []
    state.energy = 3
    res = state.play_card(0)
    check("damage 3", state.target_hp == 27)
    check("tarik 1 tambahan", res.cards_drawn == 1 and len(state.hand) == 1)


def test_reshuffle() -> None:
    print("== reshuffle ==")
    pile = CombatPile([], rng=random.Random(1))
    pile.discard_pile = [Card("Punch"), Card("Rest"), Card("Punch")]
    drawn = pile.draw_cards(2)
    check("tarik 2 dari hasil kocokan", drawn == 2 and len(pile.hand) == 2)
    check("discard kosong setelah dikocok", pile.discard_count == 0)


def test_hand_limit() -> None:
    print("== batas tangan ==")
    pile = CombatPile([Card("Punch") for _ in range(20)], rng=random.Random(2))
    pile.hand = [Card("Rest") for _ in range(10)]
    drawn = pile.draw_cards(5)
    check("tangan penuh: tidak tarik", drawn == 0 and len(pile.hand) == 10)


def test_kill_coins() -> None:
    print("== kill + koin ==")
    state = fresh_state()
    assert state.pile is not None
    state.pile.hand = [Card("Punch")]
    state.target_hp = 5
    state.energy = 3
    res = state.play_card(0)
    check("kill", res.killed and state.stage_cleared)
    check("HP clamp 0", state.target_hp == 0)
    check("+15 koin", state.coins == 15 and res.coins_earned == 15)


def test_greed_bonus() -> None:
    print("== bonus Greed ==")
    state = fresh_state()
    assert state.pile is not None
    state.pile.hand = [Card("Greed")]
    state.target_hp = 2
    state.energy = 3
    res = state.play_card(0)
    check("kill via Greed", res.killed)
    check("+30 koin (15+15)", state.coins == 30)


def test_end_turn_game_over() -> None:
    print("== end turn & game over ==")
    state = fresh_state()
    assert state.pile is not None
    state.target_hp = 30  # tidak dibunuh
    r1 = state.end_turn()
    check("turn 1 -> 2", r1 == "next_turn" and state.turn == 2)
    check("energi reset 3", state.energy == 3)
    check("tangan diisi lagi 5", len(state.hand) == 5)
    state.end_turn()
    r3 = state.end_turn()
    check("turn 3 selesai -> game over", r3 == "game_over" and state.run_over)


def test_shop() -> None:
    print("== shop ==")
    state = fresh_state()
    assert state.pile is not None
    # Menangkan stage dulu.
    state.pile.hand = [Card("Heavy Smash")]
    state.target_hp = 10
    state.energy = 3
    state.play_card(0)
    check("menang beri 15 koin", state.coins == 15)
    slots = state.open_shop()
    check("2 slot berbeda", len(slots) == 2 and slots[0] != slots[1])
    ok, _ = state.buy_shop_card(0)
    check("beli slot 1 (10 koin)", ok and state.coins == 5)
    check("slot 1 kosong", state.shop_slots[0] is None)
    check("deck 10 -> 11", len(state.master_deck) == 11)
    ok2, _ = state.buy_shop_card(1)
    check("koin 5 tidak cukup beli", not ok2)
    # Jasa hapus: deck index 0.
    deck_size = len(state.master_deck)
    ok3, _ = state.remove_deck_card(0)
    check("hapus kartu (5 koin)", ok3 and state.coins == 0)
    check("deck berkurang 1", len(state.master_deck) == deck_size - 1)
    check("harga hapus naik 5->10", state.remove_cost == 10)
    # Guard deck minimal.
    small = GameState(rng=random.Random(3))
    small.start_run()
    small.master_deck = MasterDeck([Card("Punch") for _ in range(5)])
    small.stage_cleared = True
    small.coins = 100
    ok4, _ = small.remove_deck_card(0)
    check("deck 5 kartu: hapus ditolak", not ok4)


def main() -> int:
    """Jalankan semua tes, kembalikan exit code."""
    tests = [
        test_starter_deck,
        test_hp_scaling,
        test_start_stage,
        test_play_punch,
        test_insufficient_energy,
        test_rest_no_effect,
        test_adrenaline,
        test_quick_jab_draw,
        test_reshuffle,
        test_hand_limit,
        test_kill_coins,
        test_greed_bonus,
        test_end_turn_game_over,
        test_shop,
    ]
    for test in tests:
        try:
            test()
        except Exception:
            global FAIL
            FAIL += 1
            print(f"  [ERROR] {test.__name__}")
            traceback.print_exc()
    print(f"\nHasil: {PASS} lolos, {FAIL} gagal")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
