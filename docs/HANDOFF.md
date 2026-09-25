# Handoff — Pukulin Aja

Tanggal: 21 Sep 2026. Status: **prototipe lengkap dan playable** (Fase 1–4 selesai + polish).

## Identitas
- Game deckbuilder arcade kasual (Python 3.11+, Pygame 2.x, tanpa dependency lain).
- Mouse klik kiri saja. Window 1920x1080 resizable, 60 FPS.
- State machine: `MENU -> ENCOUNTER -> SHOP -> ENCOUNTER ... -> GAME_OVER`.

## Struktur
- `main.py` (state machine), `config.py` (angka balance + palet warna), `cards.py` (`Card` + factory),
  `deck.py` (`MasterDeck`/`CombatPile`), `game_state.py` (`GameState` + `Phase`, tanpa pygame),
  `ui.py` (`Button` primer pink/sekunder putih, `FontSet`, `draw_card`, `FloatingText`),
  `states/` (menu, encounter, shop, game_over — pola `run`/`draw`/`handle_click` seragam).
- `tests/test_phase1.py` — 49 asersi headless. `docs/` — GDD aktif (`GDD_Pukulin_Aja.md`) + arsip GDD lama.

## Cara jalan (dari root proyek)
- `python main.py` — main game.
- `python -m tests.test_phase1` — tes logika (harus 49/49).

## Keputusan penting (menyimpang dari GDD awal — GDD aktif sudah diselaraskan)
1. Resolusi **1920x1080** (GDD awal 1280x720), window resizable via `SCALED|RESIZABLE`.
2. Palet **hitam–pink–putih, tanpa biru**. Tombol aksi pink; tombol netral (Start/Quit/Restart/Menu/Hapus/dll.) putih, hover pink muda, pressed pink tua, teks hitam.
3. Tambahan polish di luar spek awal: kartu hover naik 10px, angka damage melayang, HP bar flash putih, pesan reward di Shop (`GameState.last_reward`).
4. Shop tanpa kartu yang sama di 2 slot; harga hapus 5 +5 persisten; kunci hapus jika deck ≤ 5.

## Batasan / utang teknis
- Window 1920x1080 kepotong di layar < 1080p (belum ada auto-fit).
- Smoke test headless ada di folder temp IDE (bukan di repo); skenario: klik Start→kartu→End Turn, alur Shop, kalah→restart.
- Tanpa audio/aset eksternal (sesuai spek).

## Lanjut di sesi baru
Tunjuk AI ke `docs/GDD_Pukulin_Aja.md` + file ini, lalu sebutkan target perubahan. Angka balance hanya di `config.py`.
