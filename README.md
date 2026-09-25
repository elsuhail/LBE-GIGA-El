# Pukulin Aja

Deckbuilder arcade klasik. Hancurkan Target sebelum Turn habis,
belanja kartu di Shop, maju Stage sampai tumbang.

## Cara jalan

```bash
pip install -r requirements.txt
python main.py
```

## Kontrol

- Mouse klik kiri saja (window 1920x1080, bisa di-resize).
- Ikon speaker pojok kanan atas = mute di semua layar.

## Struktur

```
main.py  config.py  cards.py  deck.py  game_state.py  ui.py  audio.py
states/ (menu, encounter, shop, game_over)
assets/ (UI, audio, fonts)  docs/ (GDD)
```

## Catatan
- Detail desain: `docs/GDD_Pukulin_Aja.docx`.
