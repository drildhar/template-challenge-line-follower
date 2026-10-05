# Mengirim dan menjalankan program ke hub lewat Bluetooth.
#
# Kenapa tidak memakai `pybricksdev run ble` langsung?
#
# pybricksdev meneruskan service_uuids=[PYBRICKS_SERVICE_UUID] ke BleakScanner.
# Di BlueZ 5.87 (CachyOS, Arch, dan distro lain yang sudah memutakhirkannya)
# jalur itu rusak: pemindaiannya selesai dengan
#
#     bleak.exc.BleakDBusError: [org.bluez.Error.Failed] No discovery started
#
# dan perangkatnya sering tidak pernah ketemu. Penyebabnya, pada StopDiscovery
# bleak hanya memaafkan org.bluez.Error.NotReady, sedangkan BlueZ 5.87
# mengembalikan org.bluez.Error.Failed dengan pesan "No discovery started".
# Bug ini ada di pybricksdev 2.3.2 dan bleak 3.0.2, bukan di program robotnya.
#
# Skrip ini memindai tanpa parameter itu, mencocokkan nama hub sendiri, lalu
# memakai PybricksHubBLE milik pybricksdev untuk mengirim dan menjalankan
# program. Sisanya sama, termasuk progress bar dan keluaran print dari hub.
#
# Pakai:
#     ./.venv/bin/python kirim.py main.py
#     ./.venv/bin/python kirim.py kalibrasi.py --name "Marin Kitagawa"
#
# Atau lewat VS Code: Ctrl + Shift + B untuk main.py, atau Tasks: Run Task
# untuk program lain.
#
# Kalau muncul "hub tidak ketemu" padahal lampu hub berkedip biru, penyebab
# yang paling sering: hub sedang tersambung ke perangkat lain. Hub hanya
# menerima satu sambungan Bluetooth pada satu waktu, dan selama tersambung
# dia berhenti mengiklankan dirinya, jadi tidak terlihat oleh pemindaian.
# Tutup tab code.pybricks.com, atau minta yang sedang memakai hub itu
# memutuskan sambungannya.

import argparse
import asyncio
import sys

from bleak import BleakScanner
from bleak.exc import BleakDBusError

from pybricksdev.connections.pybricks import PybricksHubBLE

# Dipakai kalau --name tidak diberikan.
DEFAULT_NAME = "Marin Kitagawa"

# Berapa kali mencoba memindai sebelum menyerah. Hub kadang baru terlihat
# pada percobaan kedua.
SCAN_ATTEMPTS = 3
SCAN_SECONDS = 8.0


async def find_hub(name, attempts=SCAN_ATTEMPTS, seconds=SCAN_SECONDS):
    """Cari hub berdasarkan namanya, tanpa filter service_uuids.

    Mengembalikan (device, advertisement) atau None.
    """
    for attempt in range(1, attempts + 1):
        found = []

        def callback(device, adv):
            # adv.local_name baru terisi setelah scan response diterima, dan
            # device.name berasal dari properti BlueZ yang sudah tersimpan.
            # Pakai keduanya supaya hub tidak terlewat.
            label = adv.local_name or device.name or ""
            if label.upper() == name.upper():
                found.append((device, adv))

        try:
            async with BleakScanner(detection_callback=callback):
                waited = 0.0
                while waited < seconds and not found:
                    await asyncio.sleep(0.25)
                    waited += 0.25
        except BleakDBusError as ex:
            # BlueZ 5.87 mengeluh saat discovery ditutup. Kalau perangkatnya
            # sudah ketemu, pemindaiannya sebenarnya sudah berhasil.
            if not found:
                print("  pemindaian gagal:", ex)
            else:
                print("  (error saat menutup pemindai diabaikan:", ex, ")")

        if found:
            return found[0]

        print("  percobaan", attempt, "dari", attempts, "belum ketemu")

    return None


async def main():
    parser = argparse.ArgumentParser(
        description="Kirim dan jalankan program Pybricks ke hub lewat Bluetooth."
    )
    parser.add_argument("file", help="berkas program, misalnya main.py")
    parser.add_argument(
        "--name",
        default=DEFAULT_NAME,
        help="nama hub, default: %(default)s",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="jangan tunggu program selesai, langsung putuskan sambungan",
    )
    args = parser.parse_args()

    print("mencari", args.name, "...")
    hit = await find_hub(args.name)

    if hit is None:
        print()
        print("hub tidak ketemu setelah", SCAN_ATTEMPTS, "percobaan.")
        print("Periksa satu per satu:")
        print("  1. Hub menyala, dan lampu di sekeliling tombol tengah")
        print("     berkedip biru.")
        print("  2. Hub tidak sedang tersambung ke perangkat lain. Hub hanya")
        print("     menerima satu sambungan Bluetooth, dan selama tersambung")
        print("     dia berhenti mengiklankan dirinya. Tutup tab")
        print("     code.pybricks.com kalau masih terbuka.")
        print("  3. Nama hub di perintah ini sama persis dengan nama yang")
        print("     kalian beri saat memasang firmware. Huruf besar dan")
        print("     kecilnya ikut dihitung.")
        print("  4. Tidak menyambungkan hub lewat menu Bluetooth sistem.")
        print("     Kalau pernah, hapus hub dari daftar itu.")
        return 1

    device, adv = hit
    print(
        "ketemu:",
        device.address,
        "|",
        adv.local_name or device.name,
        "| rssi",
        adv.rssi,
        "dBm",
    )

    hub = PybricksHubBLE(device)
    await hub.connect()
    print("tersambung. mengirim", args.file)

    try:
        await hub.run(args.file, wait=not args.no_wait, print_output=True)
    finally:
        try:
            await hub.disconnect()
        except Exception:
            pass
        print("sambungan diputus")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\ndibatalkan")
        sys.exit(130)
