# Game Design Document (GDD): Pukulin Aja

## 0. Informasi Proyek

- **Judul:** Pukulin Aja
- **Genre:** Deckbuilder / Card Battler, arcade kasual, single-player, turn-based
- **Platform:** PC desktop (Windows / macOS / Linux)
- **Engine / Framework:** Pygame 2.x
- **Bahasa Pemrograman:** Python 3.11+
- **Resolusi & FPS:** 1920x1080, 60 FPS, window resizable
- **Input:** Mouse only (klik kiri)
- **Art Style:** Placeholder. Kotak berwarna dan teks (`pygame.draw` + font default), tanpa aset eksternal dan tanpa audio di versi 1. Tema warna: hitam, pink, putih (lihat bagian 9)
- **Durasi Satu Run:** Sekitar 10-15 menit
- **Scope:** Prototipe MVP, solo developer
- **Alur State:** MENU -> ENCOUNTER -> SHOP -> (ulang ke ENCOUNTER) -> GAME_OVER
- **Referensi:** Slay the Spire (siklus draw/discard/reshuffle dan fitur hapus kartu di Shop)

---

## 1. Konsep Utama (Elevator Pitch)

Game arcade deckbuilder kasual di mana pemain menggunakan tumpukan kartu aksi untuk menghancurkan Target statis (seperti Brankas atau Tembok) ber-HP tinggi dalam batas giliran (Turn) yang ketat. Fokus permainan murni pada manajemen Energi, efisiensi damage, dan modifikasi isi deck di fase Toko. Game bersifat endless: pemain terus maju dari Stage ke Stage sampai gagal, dan skor adalah Stage tertinggi yang dicapai. Skala game didesain seringkas mungkin agar ideal dibangun menggunakan Pygame.

---

## 2. Core Gameplay Loop

Siklus permainan berjalan linear, berulang dari satu Stage ke Stage berikutnya hingga pemain kehabisan Turn.

1. **Encounter Phase:** Pemain berhadapan dengan Target baru. Semua kartu (draw pile, discard pile, tangan) dikumpulkan dan dikocok menjadi satu draw pile. Di awal setiap Turn, pemain menarik 5 kartu dari draw pile ke tangan.
2. **Action Phase:** Pemain memainkan kartu menggunakan Energi untuk mengurangi HP Target. Tombol "End Turn" selalu aktif dan bisa ditekan kapan saja. Saat End Turn ditekan, semua sisa kartu di tangan masuk ke discard pile dan Turn berikutnya dimulai.
3. **Resolution Phase:** Jika Target HP mencapai 0 (kapan pun, termasuk di tengah Turn): Pemain menang, mendapatkan Koin, dan masuk ke Shop. Jika Turn ke-3 selesai dan Target HP > 0: Game Over.
4. **Shop Phase:** Pemain membelanjakan Koin untuk memperkuat deck (membeli kartu baru atau membuang kartu ampas). Setelah selesai, lanjut ke Stage berikutnya dengan Target yang lebih kuat.

---

## 3. Atribut & Sumber Daya (Game State)

Kalkulasi menggunakan integer mutlak, tanpa pecahan atau modifier rumit.

- **Target HP:** Dimulai dari 30 HP (Stage 1). Setiap naik Stage, Max HP bertambah 15 (30 -> 45 -> 60 -> 75 -> 90 dst.). HP Target tidak pernah kurang dari 0.
- **Turn Limit:** Selalu 3 Turn per Stage.
- **Energi:** Pemain mendapat 3 Energi di awal setiap Turn (reset ke 3, bukan ditambah). Energi tidak bisa ditabung ke giliran berikutnya.
- **Koin (Gold):** Pemain mulai dengan 0 Koin. Pemain mendapat 15 Koin setiap berhasil menghancurkan Target di suatu Stage. Koin dibawa (carry over) ke Stage berikutnya.
- **Draw per Turn:** 5 kartu di awal setiap Turn.
- **Batas Tangan:** Maksimal 10 kartu. Jika tangan penuh, kartu tambahan tidak ditarik.
- **Siklus Deck:** Kartu yang dimainkan masuk ke discard pile. Sisa tangan saat End Turn juga masuk ke discard pile. Jika draw pile kosong saat harus menarik kartu, discard pile dikocok menjadi draw pile baru. Jika keduanya kosong, tidak ada kartu yang ditarik.

---

## 4. Roster Kartu (Tahap Prototipe)

Setiap kartu hanya memiliki tiga parameter: Nama, Cost (Biaya Energi), dan Efek. Karena Target hanya satu, klik kartu langsung memainkannya tanpa memilih target. Kartu yang Cost-nya melebihi Energi saat ini tidak bisa dimainkan.

### Starter Deck (10 Kartu Awal)

| Kartu | Jumlah | Cost | Efek |
|-------|--------|------|------|
| Punch | x6 | 1 | Damage 5 |
| Rest | x4 | 0 | Tidak ada efek (kartu ampas untuk memperlambat tempo) |

### Pool Kartu Shop (Bisa Dibeli)

| Kartu | Cost | Efek |
|-------|------|------|
| Heavy Smash | 3 | Damage 25 |
| Double Strike | 2 | Damage 12 |
| Adrenaline | 0 | Tambah +2 Energi |
| Quick Jab | 1 | Damage 3. Otomatis menarik 1 kartu tambahan dari deck ke tangan saat dimainkan (mengikuti aturan Siklus Deck dan Batas Tangan) |
| Greed | 1 | Damage 2. Jika serangan dari kartu ini membuat HP Target menjadi 0, pemain mendapat bonus +15 Koin |

---

## 5. Sistem Shop (Deck Manipulation)

Antarmuka Toko hanya menampilkan tiga slot interaksi yang di-generate setiap akhir Stage.

- **Slot Beli 1:** Menawarkan 1 kartu acak dari Pool (Harga: 10 Koin).
- **Slot Beli 2:** Menawarkan 1 kartu acak dari Pool (Harga: 10 Koin). Tidak boleh kartu yang sama dengan Slot Beli 1.
- **Jasa Hapus (Remove):** Membuang 1 kartu pilihan dari deck secara permanen. Harga awal 5 Koin, dan harganya meningkat +5 Koin setiap kali jasa ini digunakan. Harga ini persisten sepanjang satu run. Tidak bisa digunakan jika deck berisi 5 kartu atau kurang.
- Kartu yang dibeli langsung masuk ke deck, dan slotnya menjadi kosong (tidak bisa dibeli lagi).
- Tombol beli atau hapus yang tidak terjangkau Koin ditampilkan abu-abu dan tidak bisa diklik.
- Tombol "Next Stage" digunakan untuk lanjut ke Stage berikutnya.

---

## 6. Kondisi Akhir Game

- Game Over terjadi jika Turn ke-3 selesai dan Target HP masih di atas 0.
- Game bersifat endless, tidak ada Stage terakhir.
- **Skor:** Stage tertinggi yang berhasil dicapai.
- Layar Game Over menampilkan skor, dengan tombol "Restart" (mulai run baru) dan "Menu" (kembali ke menu utama).

---

## 7. Layout Antarmuka (UI)

Semua elemen memakai kotak berwarna dan teks sederhana.

- **Menu:** Judul game, tombol "Start" dan "Quit".
- **Encounter:**
  - Target di tengah atas: nama, HP bar, dan angka HP (contoh: 30/30).
  - Nama Target berganti tiap Stage (Brankas, Tembok, dst.), hanya kosmetik.
  - Kartu di tangan berjajar di bagian bawah. Setiap kartu menampilkan Nama, Cost, dan Efek.
  - Kartu yang tidak cukup Energi ditampilkan redup dan tidak bisa diklik.
  - Info di sudut layar: Stage, Turn (x/3), Energi, Koin, jumlah kartu di draw pile dan discard pile.
  - Tombol "End Turn" di kanan bawah.
- **Shop:** Tiga slot (Beli 1, Beli 2, Hapus) di tengah, tampilan Koin, dan tombol "Next Stage". Untuk Jasa Hapus, pemain memilih kartu dari daftar deck.
- **Game Over:** Sesuai bagian 6.

---

## 8. Catatan Teknis (Untuk Implementasi)

- Arsitektur state machine sederhana: MENU, ENCOUNTER, SHOP, GAME_OVER.
- Logika game dipisah dari rendering agar bisa dites tanpa membuka window.
- Semua angka balance (HP awal, pertambahan HP, Turn Limit, Energi, Koin, harga Shop, isi deck awal) dan semua warna (bagian 9) disimpan di satu file `config.py`.
- Struktur file: `main.py`, `config.py`, `cards.py`, `deck.py`, `game_state.py`, `ui.py`, folder `states/` (`menu.py`, `encounter.py`, `shop.py`, `game_over.py`), folder `tests/` (`test_phase1.py`), dan folder `docs/` (dokumen GDD).

---

## 9. Color Palette

Tema: **Hitam, Pink, Putih.** Hitam sebagai dasar gelap, pink sebagai warna aksi utama, putih untuk kartu dan teks. Tidak ada warna di luar palette ini, kecuali abu-abu redup untuk kondisi disabled.

### 9.1 Warna Dasar

| Nama | Hex | RGB | Fungsi |
|------|-----|-----|--------|
| Black (Background) | `#0F0F0F` | (15, 15, 15) | Background seluruh layar |
| Panel Dark | `#1E1E24` | (30, 30, 36) | Panel info, slot Shop, HP bar kosong, baris daftar deck |
| White | `#FFFFFF` | (255, 255, 255) | Body kartu, tombol putih, teks di atas gelap |
| Off-White | `#F5F5FA` | (245, 245, 250) | Teks sekunder, border baris netral |

### 9.2 Pink (Warna Aksi Utama)

| Nama | Hex | RGB | Fungsi |
|------|-----|-----|--------|
| Pink | `#FF4FA3` | (255, 79, 163) | Tombol aksi utama, border kartu dan panel, isi HP bar, badge Cost, angka damage melayang, baris deck terpilih |
| Pink Light | `#FF8CC6` | (255, 140, 198) | State hover semua tombol dan kartu, angka Koin |
| Pink Dark | `#C2337A` | (194, 51, 122) | State ditekan (pressed) semua tombol |

### 9.3 Disabled

| Nama | Hex | RGB | Fungsi |
|------|-----|-----|--------|
| Disabled Fill | `#4A4A5E` | (74, 74, 94) | Tombol atau kartu yang tidak bisa diklik |
| Disabled Text | `#8A8AA0` | (138, 138, 160) | Teks pada elemen disabled |

### 9.4 Pemakaian per Elemen UI

| Elemen | Warna |
|--------|-------|
| Background layar | Black |
| Judul game dan judul layar | Pink di atas Black |
| Body kartu | White, border 2px Pink |
| Nama dan teks efek kartu | Black (satu warna untuk semua jenis efek) |
| Badge Cost (pojok kartu) | Fill Pink, angka Black |
| Kartu tidak cukup Energi | Disabled Fill, teks Disabled Text |
| Kartu hover | Border berubah ke Pink Light, kartu naik 10px |
| HP bar | Kosong Panel Dark, isi Pink, border White |
| Flash damage masuk | Isi HP bar berkedip White singkat |
| Angka damage melayang | Teks Pink di dekat Target |
| Teks Energi | White |
| Teks Koin | Pink Light |
| Teks Stage, Turn, jumlah draw/discard, pesan aksi | White |
| Teks sekunder (subjudul, catatan) | Off-White |
| Tombol aksi (End Turn, Beli, Next Stage) | Fill Pink, teks Black. Hover Pink Light. Pressed Pink Dark |
| Tombol netral (Start, Quit, Restart, Menu, Hapus, Kembali, <<, >>) | Fill White, teks Black. Hover Pink Light. Pressed Pink Dark |
| Tombol disabled | Disabled Fill, teks Disabled Text |
| Slot Shop | Panel Dark, border Pink |
| Slot Shop kosong (sudah dibeli) | Panel Dark, border Disabled Fill, teks Disabled Text |
| Panel Jasa Hapus dan Game Over | Panel Dark, border Pink |
| Baris daftar deck (mode hapus) | Border Off-White. Hover Pink Light. Terpilih Pink |

### 9.5 Catatan Kontras

- Teks pada tombol Pink dan White memakai **Black**, bukan White, supaya kontras cukup tinggi dan mudah dibaca.
- Teks pada Black dan Panel Dark memakai **White** atau **Off-White**.
- Teks pada body kartu putih memakai **Black**.

### 9.6 Kode untuk `config.py`

```python
# Warna (RGB) - Tema Hitam / Pink / Putih. Tanpa biru.
BLACK        = (15, 15, 15)
PANEL_DARK   = (30, 30, 36)
WHITE        = (255, 255, 255)
OFF_WHITE    = (245, 245, 250)

PINK         = (255, 79, 163)
PINK_LIGHT   = (255, 140, 198)
PINK_DARK    = (194, 51, 122)

DISABLED_FILL = (74, 74, 94)
DISABLED_TEXT = (138, 138, 160)
```
