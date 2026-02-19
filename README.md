# NUSANTARA BOT - for wolfbet

Developer: **cipow**

Bot ini membaca konfigurasi dari `config.json`, lalu menjalankan auto betting dice langsung ke API Wolfbet sesuai dokumentasi di `swagger.json`.

## Endpoint API yang dipakai

- `GET /user/balances`
- `POST /bet/place`
- `GET /game/seed/refresh` (opsional)
- `POST /user/seed/refresh` (opsional)

Base URL default:

`https://wolfbet.com/api/v1`

## Setup di Termux

1. Install Python dan git:

```bash
pkg update && pkg upgrade -y
pkg install python git -y
```

2. Masuk ke folder project, lalu install dependency:

```bash
pip install -r requirements.txt
```

3. Edit `config.json`, isi:
- `api.token` dengan API token Wolfbet kamu.
- blok `simple` sesuai kebutuhan (setting inti).

4. Jalankan bot:

```bash
python main.py
```

## Konfigurasi penting (`config.json`)

### `api`
- `token`: API token Wolfbet (wajib diisi).
- `retry_count`: jumlah retry kalau koneksi/API error.
- `rate_limit_wait_seconds`: cooldown saat rate limit.

### `simple` (disarankan)
Gunakan blok ini untuk setting cepat seperti tampilan panel dice pada gambar. Cukup isi poin inti:

- `enabled`: `ON/OFF` untuk pakai mode simple.
- `currency`: contoh `trx`, `doge`, `btc`.
- `hilo_fixed`: pilih `HI` atau `LOW` (dipakai saat random OFF).
- `hilo_random`: `ON/OFF` untuk random `HI/LOW` (under/over) tiap bet.
- `bet_amount`: nominal bet dasar.
- `multiplier`: multiplier target.
  - Pada mode simple, `bet_value/chance` disinkronkan otomatis di backend dari nilai ini.
  - Nilai sinkronisasi internal disimpan di backend bot, tidak perlu setting manual di config.
- `chance_random`: `ON/OFF` untuk random chance tiap bet.
- `chance_random_min` / `chance_random_max`: range chance random (%).
- `chance_random_precision`: presisi desimal chance random.
  - Saat `chance_random=ON`, multiplier akan ikut dihitung otomatis dari chance random setiap bet.
- `system`: preset inti 10 pilihan (`martingale`, `fibonacci`, `paroli`, `anti_martingale`, `dalembert`, `flat`, `mining`, `mining_v2`, `pro_safe`, `pro_recovery`, `custom`).
  - Nama preset lama (`premium`, `premium_guard`, `premium_compound`, `pro_scalper`, `long_run_guard`, `anti_losstrack`) tetap diterima sebagai alias kompatibilitas.
- `preset_prompt`: `ON/OFF`. Saat start bot akan konfirmasi preset yang ingin dijalankan (bisa tetap sesuai config atau pilih lain seperti Fibonacci, dll).
  - Tekan `Enter` atau pilih `0` untuk tetap pakai preset dari `system` pada config.
- `reset_if_win` / `reset_if_loss`: reset amount ke base setelah win/loss.
- `increase_after_win_percent` / `increase_after_loss_percent`: kenaikan amount dalam persen.
- `max_bet_stop`: stop jika amount melebihi nilai ini (`0` nonaktif).
- `balance_stop`: stop jika balance <= nilai ini (`0` nonaktif).
- `profit_stop`: stop jika total profit >= nilai ini (`0` nonaktif).
- `stop_loss`: stop jika total loss menyentuh nilai ini (`0` nonaktif).
- `max_bets`: jumlah maksimal bet (`0` nonaktif).
- `bet_interval_ms`: jeda bet dalam ms (`1000` = 1 detik).
- `replay_on_take_profit`: `ON/OFF`, auto jalan lagi jika stop karena take profit.
- `replay_on_stop_loss`: `ON/OFF`, auto jalan lagi jika stop karena stop loss.
- `replay_after_sec`: jeda detik sebelum replay.
- `replay_count`: jumlah replay otomatis maksimal untuk kondisi replay yang aktif (TP/SL).

Parameter detail preset tetap ada di backend (`strategy.preset.*`) dan otomatis dipakai saat pilih `system`.

Contoh simple config:

```json
"simple": {
  "enabled": "ON",
  "currency": "trx",
  "hilo_fixed": "LOW",
  "hilo_random": "OFF",
  "bet_amount": 0.00000001,
  "multiplier": 1.98,
  "chance_random": "OFF",
  "chance_random_min": 40.0,
  "chance_random_max": 60.0,
  "chance_random_precision": 2,
  "system": "mining_v2",
  "preset_prompt": "ON",
  "reset_if_win": "ON",
  "reset_if_loss": "OFF",
  "increase_after_win_percent": 0,
  "increase_after_loss_percent": 100,
  "max_bet_stop": 0,
  "balance_stop": 0,
  "profit_stop": 0,
  "stop_loss": 0,
  "max_bets": 0,
  "bet_interval_ms": 1000,
  "replay_on_take_profit": "OFF",
  "replay_on_stop_loss": "OFF",
  "replay_after_sec": 5,
  "replay_count": 0
}
```

### Advanced (opsional)
Jika butuh kontrol penuh, kamu tetap bisa pakai blok `bot`, `strategy`, dan `display`.
Saat `simple.enabled = "ON"`, nilai inti dari `simple` akan diprioritaskan.

### `display`
- `history_style`: `mining` (tabel compact) atau `classic`.
- `history_header_every`: interval cetak ulang header tabel.
- `history_width`: `0` = auto ikut lebar terminal.
- `coin_decimal_places`: jumlah maksimal desimal untuk nilai coin (`0-8`).
- `amount_display_precision`, `profit_display_precision`, `balance_display_precision`:
  presisi tampilan (tidak boleh lebih dari `coin_decimal_places`).
- `sticky_stats_footer`: `ON/OFF`, menampilkan statistik live tetap di bawah terminal.
  Pada mode `mining`, tabel `TIME | ROLL | WIN/LOSS | MULTI | AMOUNT | PROFIT | BALANCE <COIN> | TOTAL PROFIT`
  ditampilkan di panel bawah (sticky), bukan di setiap baris log bet.
- `balance_sync_mode`:
  - `hybrid` (disarankan): pakai API kalau update, fallback ke estimasi lokal kalau API tampak stagnan.
  - `api`: selalu pakai nilai `user_balance` dari API.
  - `estimated`: selalu pakai hitungan lokal `balance + profit`.
- `balance_refresh_every`: interval sinkronisasi ulang balance live dari endpoint `/user/balances`.
- `show_idr_value`: `ON/OFF`, tampilkan konversi nilai ke Rupiah (`Rp`) secara live.
- `idr_refresh_seconds`: interval refresh harga coin -> IDR (source: CoinGecko).

Format panel sticky (bawah):

`TIME | ROLL | WIN/LOSS | MULTI | AMOUNT | PROFIT | BALANCE <COIN> | TOTAL PROFIT`

Saat `show_idr_value=ON`, footer juga akan menampilkan estimasi nilai Rupiah (`IDR BAL` dan `IDR TOT`) yang terhitung otomatis dari harga live.
Untuk `history_style: mining`, baris log bet juga menampilkan `profit IDR` per bet secara otomatis.

## Catatan

- Pastikan token valid dari halaman API settings akun Wolfbet.
- Gunakan nominal kecil dulu untuk test.
- Tema warna default sudah dioptimalkan untuk layar AMOLED Termux (clean: cyan/yellow/white) supaya lebih nyaman dipakai lama.
- Jika API mengembalikan error/rate limit, bot sudah punya retry dan cooldown.
- Jika muncul error `Incorrect win chance given`, itu artinya `multiplier` dan `bet_value` tidak cocok.
  Bot versi ini akan auto sinkronisasi pair tersebut.
- Tidak ada strategi yang bisa menjamin anti-loss 100% atau saldo selalu naik; pakai stop loss, max amount, dan test kecil dulu.
