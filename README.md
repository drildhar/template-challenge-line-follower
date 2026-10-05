# Template Tantangan Robot Pengikut Garis

Titik awal untuk Tantangan Robot Pengikut Garis, [EF234726] Robotika Kelas T. Isinya pengikut garis PD yang sudah jalan, sama dengan program lengkap di bagian 9 `pengikut-garis.md`. Manuver di depan dinding berwarna belum ada. Itu bagian tantangan kalian.

| File | Isi |
|---|---|
| `perangkat.py` | Port motor dan sensor, serta ukuran roda. Dipakai bersama oleh kedua program |
| `main.py` | Pengikut garis. Ini program yang didemonstrasikan |
| `kalibrasi.py` | Mengukur `BLACK` dan `WHITE` untuk `main.py` |
| `kalibrasi_dinding.py` | Mengangkat sensor lalu menampilkan jarak dan warna dinding untuk menyetel `WALL_MM`, `READ_MM`, dan `ARM_UP_DEG` |
| `.vscode/tasks.json` | Tombol pintas untuk mengirim program ke hub |
| `requirements.txt` | `pybricksdev` dan `pybricks` |

## Persiapan

Hub harus sudah terpasang firmware Pybricks. Kalau belum, ikuti bagian 2 `instalasi-pybricks.md`.

1. Buat repo kalian dari template ini lewat tombol Use this template, lalu clone dan buka foldernya di VS Code. Pengguna Windows, jangan buka lewat WSL.
2. Buat environment dan pasang paketnya. Dengan pip:

   ```bash
   python -m venv .venv
   ```

   Aktifkan dengan `.venv\Scripts\Activate.ps1` di Windows, atau `source .venv/bin/activate` di macOS dan Linux, lalu:

   ```bash
   pip install -r requirements.txt
   ```

   Pengguna conda, uv, dan pixi, ikuti jalurnya di bagian 3.2 `instalasi-pybricks.md`. Dengan uv, cukup `uv venv` lalu `uv pip install -r requirements.txt`.
3. Di VS Code, pilih interpreter environment tadi lewat Python: Select Interpreter.
4. Ganti `Kancil` di `.vscode/tasks.json` dengan nama hub kalian. Ada dua tempat.
5. Sesuaikan port dan ukuran roda di `perangkat.py` dengan robot kalian.

## Menjalankan

Nyalakan hub sampai lampunya berkedip biru, lalu:

| Mau menjalankan | Caranya |
|---|---|
| `main.py` | `Ctrl` + `Shift` + `B` |
| `kalibrasi.py` | `Ctrl` + `Shift` + `P`, Tasks: Run Task, pilih Pybricks: jalankan kalibrasi.py |

Dari terminal juga bisa: `pybricksdev run ble --name Kancil main.py`.

Program yang terakhir dikirim tersimpan di slot hub yang sedang terpilih. Saat demonstrasi, robot dijalankan dengan tombol tengah hub, tanpa laptop. Tombol tengah juga menghentikan program.

## Urutan kerja

1. Letakkan sensor tepat di atas garis, jalankan `kalibrasi.py`, lalu salin angkanya ke `BLACK` dan `WHITE` di `main.py`. Ulangi setiap pindah ruangan atau lintasan, termasuk saat trial di Lab KCV.
2. Jalankan `main.py`. Kalau robot langsung berputar keluar garis, balik tanda `KP` atau taruh robot di tepi garis yang satunya.
3. Setel konstanta dengan urutan di bagian 10 `pengikut-garis.md`. Ubah satu angka setiap percobaan.
4. Tambahkan manuver dinding di tempat yang ditandai komentar di awal loop `main.py`.

## Aturan dinding

| Warna dinding | Belok |
|---|---|
| Merah | Kiri |
| Hijau | Kanan |
| Kuning | Kiri atau kanan, pilihan tim |

Nilai penuh Checkpoint 2 butuh manuver benar di depan sekurang-kurangnya dua dinding. Rincian penilaian ada di buku panduan tantangan.
