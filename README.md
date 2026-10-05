# Tantangan Robot Pengikut Garis

Robot pengikut garis untuk Tantangan Robot Pengikut Garis, [EF234726] Robotika
Kelas T, Lab KCV.

Repo ini dibuat dari template `robotika-t-26/template-challenge-line-follower`.
Isi template itu pengikut garis PD yang sudah jalan. Manuver di depan dinding
berwarna **sudah ditambahkan di sini**: motor A mengangkat sensor warna supaya
menghadap depan, warnanya dibaca, lalu robot belok sesuai aturan warna.

| File | Isi |
|---|---|
| `perangkat.py` | Port motor dan sensor, ukuran roda, motor lengan. Dipakai bersama semua program |
| `main.py` | Program yang didemonstrasikan. Pengikut garis PD, pencarian garis hilang, dan manuver dinding |
| `diagnosa.py` | Mengukur kecepatan loop dan mencatat kalau sensor jarak salah mendeteksi dinding |
| `kalibrasi.py` | Mengukur `BLACK` dan `WHITE` untuk `main.py` |
| `kalibrasi_dinding.py` | Mengangkat sensor lalu menampilkan jarak dan warna dinding |
| `.vscode/settings.json` | Nama hub dan interpreter Python |
| `.vscode/tasks.json` | Tombol pintas untuk mengirim program ke hub |
| `requirements.txt` | `pybricksdev` dan `pybricks` |

## Port robot

Port ini sudah diperbaiki di commit `fix(perangkat): ports` pada template.
Jangan diubah tanpa alasan.

| Perangkat | Port |
|---|---|
| Motor kiri, `Direction.COUNTERCLOCKWISE` | E |
| Motor kanan, `Direction.CLOCKWISE` | F |
| Sensor warna | D |
| Sensor jarak, menghadap depan | C |
| Motor lengan pengangkat sensor | A |

Sudut 0 pada motor lengan berarti sensor menghadap ke lantai. Pastikan lengan
berada di posisi itu setiap kali program dimulai, karena `BLACK` dan `WHITE`
diukur pada posisi itu.

## Persiapan

1. Hub harus sudah terpasang firmware Pybricks. Kalau belum, ikuti bagian 2
   `instalasi-pybricks.md` di repo Modul-Robotika.
2. Buat environment dan pasang paketnya:

   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

   Jalur lain (pip, conda, pixi) ada di bagian 3.2 `instalasi-pybricks.md`.
3. Buka folder ini di VS Code. Interpreter `.venv` sudah diatur di
   `.vscode/settings.json`.
4. Ganti `pybricks.hubName` di `.vscode/settings.json` dengan nama hub kalian.
   Cukup satu tempat itu; keempat tugas di `tasks.json` membacanya dari sana.
5. Kalau robot kalian berbeda dari tabel port di atas, sesuaikan `perangkat.py`.

## Menjalankan

Nyalakan hub sampai lampunya berkedip biru, lalu:

| Mau menjalankan | Caranya |
|---|---|
| `main.py` | `Ctrl` + `Shift` + `B` |
| program lain | `Ctrl` + `Shift` + `P`, Tasks: Run Task, pilih namanya |

Dari terminal:

```bash
./.venv/bin/pybricksdev run ble --name "Marin Kitagawa" main.py
```

Tanda kutipnya wajib karena nama hubnya mengandung spasi.

Program yang terakhir dikirim tersimpan di slot hub yang sedang terpilih. Saat
demonstrasi, robot dijalankan dengan tombol tengah hub, tanpa laptop. Tombol
tengah juga menghentikan program.

## Urutan kerja

Kerjakan berurutan. Setiap langkah memakai hasil langkah sebelumnya.

1. **Periksa rakitan.** Tiga uji di bagian 2.4 `pengikut-garis.md`. Rangka yang
   goyang tidak bisa diselamatkan oleh penguatan sehebat apa pun.
2. **Ukur hitam dan putih.** Jalankan `kalibrasi.py`, salin `BLACK` dan `WHITE`
   ke `main.py`. Ulangi setiap pindah ruangan atau lintasan, termasuk saat trial
   di Lab KCV.
3. **Setel pengikut garis.** Urutannya di bagian 10 `pengikut-garis.md`, dengan
   `KD` masih nol. Ubah satu angka setiap percobaan, ukur hasilnya dengan waktu
   putaran.
4. **Ukur dinding.** Jalankan `kalibrasi_dinding.py`, dekatkan tiap warna
   dinding, catat jarak saat warnanya mulai terbaca benar. Angka itu untuk
   `READ_MM`. Sambil itu periksa `ARM_UP_DEG`: kalau sensor belum menghadap
   lurus ke depan saat lengan di angka itu, perbaiki angkanya.
5. **Jalankan `main.py` sampai dua dinding.** Setel `WALL_MM`, `FORWARD_MM`,
   `TURN_FIRST_DEG`, dan `SEARCH_DEG` kalau perlu.
6. **Kejar waktu tempuh.** Naikkan `BASE_SPEED` sedikit demi sedikit selama
   robot masih selesai lima kali berturut-turut.

## Kalau pengikut garisnya bagus kadang-kadang saja

Itu bukan soal `KP` atau `KD` yang salah. Nilai `KD` adalah selisih error per
satu siklus loop, jadi kalau irama loopnya berubah-ubah, `KD` yang sudah
disetel ikut berubah artinya. Bagian 6 dan bagian 11 `pengikut-garis.md`.

Penyebabnya biasanya pembacaan sensor yang memblokir loop. Di repo ini
pembacaan sensor jarak sudah dipindah supaya tidak terjadi:

```python
WALL_CHECK_EVERY = 5      # periksa dinding tiap 5 siklus, bukan tiap siklus
```

Kalau masih tidak konsisten, ukur sendiri dengan `diagnosa.py` tugas 1. Robot
diam di tempat, tidak butuh lintasan, selesai dalam 12 detik. Yang dibandingkan:

| Bentuk loop | Artinya |
|---|---|
| `wait` saja | batas atas yang mungkin |
| `+ sensor.reflection()` | seperti template asli yang sudah teruji |
| `+ distance_sensor.distance()` | seperti main.py sebelum diperbaiki |
| `+ arm.hold()` | untuk melihat biaya motor lengan |

Kalau baris ketiga jauh lebih kecil dari baris kedua, pembacaan sensor jarak
yang jadi penyebabnya, dan `WALL_CHECK_EVERY` yang menanganinya. Kalau baris
keempat turun lagi, setel `ARM_HOLD_WHILE_FOLLOWING = False` di `main.py`
supaya motor lengan tidak menahan posisinya terus.

Tugas 2 `diagnosa.py` mencatat bacaan sensor jarak di bawah `WALL_MM` selama
robot mengikuti garis. Kalau ada bacaan seperti itu padahal robot tidak sedang
menghadap dinding, robot akan berhenti dan menjalankan manuver dinding di
tengah lintasan. Naikkan `WALL_READS` atau turunkan `WALL_MM`.

## Aturan dinding

| Warna dinding | Belok |
|---|---|
| Merah | Kiri |
| Hijau | Kanan |
| Kuning | Kiri atau kanan, pilihan tim |

Nilai penuh Checkpoint 2 butuh manuver benar di depan sekurang-kurangnya dua
dinding. Rincian penilaian ada di buku panduan tantangan.

`YELLOW_TURN` dan `FALLBACK_TURN` ada di `main.py`. `FALLBACK_TURN` dipakai
kalau warnanya tidak terbaca sama sekali setelah `WALL_ATTEMPTS` percobaan.
Angkanya `RIGHT`, jadi kalau itu terjadi di dinding merah, manuver itu
nilainya nol. Perbaikan yang benar bukan mengubah angka ini, melainkan
membuat warnanya terbaca: lihat lagi `READ_MM` dan `ARM_UP_DEG`.

## Batas keselamatan

- `MAX_RUNTIME_MS` membuat robot berhenti sendiri satu menit sebelum batas
  10 menit juri.
- Tombol tengah hub menghentikan program kapan saja.
- Dua loop di `turn_to_line()` punya batas waktu. Sebelumnya, kalau roda
  tertahan dan sudut robot tidak bertambah, keduanya berputar selamanya.

## Angka yang harus diukur, bukan ditebak

Catat semuanya untuk laporan:

- `BLACK`, `WHITE`, dan kecepatan loop sebenarnya
- Tabel percobaan tuning: `KP`, `KD`, `BASE_SPEED`, waktu putaran
- Rentang jarak tempat warna dinding terbaca, dan `ARM_UP_DEG` yang benar
- Waktu tempuh lima percobaan berturut-turut yang selesai

Constanta kalian bukan sifat algoritmanya, melainkan sifat robot kalian di
lintasan itu pada hari itu. Yang bisa dipindah antar robot adalah cara
menyetelnya, bukan angkanya.
