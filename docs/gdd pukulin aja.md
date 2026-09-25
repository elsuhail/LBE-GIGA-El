Game Design Document (GDD): Pukulin Aja

0. Informasi Proyek
- Judul: Pukulin Aja
- Genre: Deckbuilder / Card Battler, arcade kasual, single-player, turn-based
- Platform: PC desktop (Windows / macOS / Linux)
- Engine / Framework: Pygame 2.x
- Bahasa Pemrograman: Python 3.11+
- Resolusi & FPS: 1280x720, 60 FPS, window tidak resizable
- Input: Mouse only (klik kiri)
- Art Style: Placeholder. Kotak berwarna dan teks (pygame.draw + font default), tanpa aset eksternal dan tanpa audio di versi 1
- Durasi Satu Run: Sekitar 10-15 menit
- Scope: Prototipe MVP, solo developer
- Alur State: MENU -> ENCOUNTER -> SHOP -> (ulang ke ENCOUNTER) -> GAME_OVER
- Referensi: Slay the Spire (siklus draw/discard/reshuffle dan fitur hapus kartu di Shop)

1. Konsep Utama (Elevator Pitch)
Game arcade deckbuilder kasual di mana pemain menggunakan tumpukan kartu aksi untuk menghancurkan Target statis (seperti Brankas atau Tembok) ber-HP tinggi dalam batas giliran (Turn) yang ketat. Fokus permainan murni pada manajemen Energi, efisiensi damage, dan modifikasi isi deck di fase Toko. Game bersifat endless: pemain terus maju dari Stage ke Stage sampai gagal, dan skor adalah Stage tertinggi yang dicapai. Skala game didesain seringkas mungkin agar ideal dibangun menggunakan Pygame.

2. Core Gameplay Loop
Siklus permainan berjalan linear, berulang dari satu Stage ke Stage berikutnya hingga pemain kehabisan Turn.
1. Encounter Phase: Pemain berhadapan dengan Target baru. Semua kartu (draw pile, discard pile, tangan) dikumpulkan dan dikocok menjadi satu draw pile. Di awal setiap Turn, pemain menarik 5 kartu dari draw pile ke tangan.
2. Action Phase: Pemain memainkan kartu menggunakan Energi untuk mengurangi HP Target. Tombol "End Turn" selalu aktif dan bisa ditekan kapan saja. Saat End Turn ditekan, semua sisa kartu di tangan masuk ke discard pile dan Turn berikutnya dimulai.
3. Resolution Phase: Jika Target HP mencapai 0 (kapan pun, termasuk di tengah Turn): Pemain menang, mendapatkan Koin, dan masuk ke Shop. Jika Turn ke-3 selesai dan Target HP > 0: Game Over.
4. Shop Phase: Pemain membelanjakan Koin untuk memperkuat deck (membeli kartu baru atau membuang kartu ampas). Setelah selesai, lanjut ke Stage berikutnya dengan Target yang lebih kuat.

3. Atribut & Sumber Daya (Game State)
Kalkulasi menggunakan integer mutlak, tanpa pecahan atau modifier rumit.
- Target HP: Dimulai dari 30 HP (Stage 1). Setiap naik Stage, Max HP bertambah 15 (30 -> 45 -> 60 -> 75 -> 90 dst.). HP Target tidak pernah kurang dari 0.
- Turn Limit: Selalu 3 Turn per Stage.
- Energi: Pemain mendapat 3 Energi di awal setiap Turn (reset ke 3, bukan ditambah). Energi tidak bisa ditabung ke giliran berikutnya.
- Koin (Gold): Pemain mulai dengan 0 Koin. Pemain mendapat 15 Koin setiap berhasil menghancurkan Target di suatu Stage. Koin dibawa (carry over) ke Stage berikutnya.
- Draw per Turn: 5 kartu di awal setiap Turn.
- Batas Tangan: Maksimal 10 kartu. Jika tangan penuh, kartu tambahan tidak ditarik.
- Siklus Deck: Kartu yang dimainkan masuk ke discard pile. Sisa tangan saat End Turn juga masuk ke discard pile. Jika draw pile kosong saat harus menarik kartu, discard pile dikocok menjadi draw pile baru. Jika keduanya kosong, tidak ada kartu yang ditarik.

4. Roster Kartu (Tahap Prototipe)
Setiap kartu hanya memiliki tiga parameter: Nama, Cost (Biaya Energi), dan Efek. Karena Target hanya satu, klik kartu langsung memainkannya tanpa memilih target. Kartu yang Cost-nya melebihi Energi saat ini tidak bisa dimainkan.

Starter Deck (10 Kartu Awal):
- Punch (x6): Cost 1, Damage 5.
- Rest (x4): Cost 0, Tidak ada efek (Kartu ampas untuk memperlambat tempo).

Pool Kartu Shop (Bisa Dibeli):
- Heavy Smash: Cost 3, Damage 25.
- Double Strike: Cost 2, Damage 12.
- Adrenaline: Cost 0, Tambah +2 Energi.
- Quick Jab: Cost 1, Damage 3. Otomatis menarik 1 kartu tambahan dari deck ke tangan saat dimainkan (mengikuti aturan Siklus Deck dan Batas Tangan).
- Greed: Cost 1, Damage 2. Jika serangan dari kartu ini membuat HP Target menjadi 0, pemain mendapat bonus +15 Koin.

5. Sistem Shop (Deck Manipulation)
Antarmuka Toko hanya menampilkan tiga slot interaksi yang di-generate setiap akhir Stage.
- Slot Beli 1: Menawarkan 1 kartu acak dari Pool (Harga: 10 Koin).
- Slot Beli 2: Menawarkan 1 kartu acak dari Pool (Harga: 10 Koin). Tidak boleh kartu yang sama dengan Slot Beli 1.
- Jasa Hapus (Remove): Membuang 1 kartu pilihan dari deck secara permanen. Harga awal 5 Koin, dan harganya meningkat +5 Koin setiap kali jasa ini digunakan. Harga ini persisten sepanjang satu run. Tidak bisa digunakan jika deck berisi 5 kartu atau kurang.
- Kartu yang dibeli langsung masuk ke deck, dan slotnya menjadi kosong (tidak bisa dibeli lagi).
- Tombol beli atau hapus yang tidak terjangkau Koin ditampilkan abu-abu dan tidak bisa diklik.
- Tombol "Next Stage" digunakan untuk lanjut ke Stage berikutnya.

6. Kondisi Akhir Game
- Game Over terjadi jika Turn ke-3 selesai dan Target HP masih di atas 0.
- Game bersifat endless, tidak ada Stage terakhir.
- Skor: Stage tertinggi yang berhasil dicapai.
- Layar Game Over menampilkan skor, dengan tombol "Restart" (mulai run baru) dan "Back to Menu".

7. Layout Antarmuka (UI)
Semua elemen memakai kotak berwarna dan teks sederhana.
- Menu: Judul game, tombol "Start" dan "Quit".
- Encounter:
  - Target di tengah atas: nama, HP bar, dan angka HP (contoh: 30/30).
  - Nama Target berganti tiap Stage (Brankas, Tembok, dst.), hanya kosmetik.
  - Kartu di tangan berjajar di bagian bawah. Setiap kartu menampilkan Nama, Cost, dan Efek.
  - Kartu yang tidak cukup Energi ditampilkan redup dan tidak bisa diklik.
  - Info di sudut layar: Stage, Turn (x/3), Energi, Koin, jumlah kartu di draw pile dan discard pile.
  - Tombol "End Turn" di kanan bawah.
- Shop: Tiga slot (Beli 1, Beli 2, Hapus) di tengah, tampilan Koin, dan tombol "Next Stage". Untuk Jasa Hapus, pemain memilih kartu dari daftar deck.
- Game Over: Sesuai bagian 6.

8. Catatan Teknis (Untuk Implementasi)
- Arsitektur state machine sederhana: MENU, ENCOUNTER, SHOP, GAME_OVER.
- Logika game dipisah dari rendering agar bisa dites tanpa membuka window.
- Semua angka balance (HP awal, pertambahan HP, Turn Limit, Energi, Koin, harga Shop, isi deck awal) disimpan di satu file config.py.
- Struktur file: main.py, config.py, cards.py, deck.py, game_state.py, ui.py, dan folder states/ (menu.py, encounter.py, shop.py, game_over.py).