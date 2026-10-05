# Alat diagnosa untuk pengikut garis.
#
# Dipakai kalau pengikut garisnya jalan bagus kadang-kadang saja, tidak
# konsisten. Tujuannya memisahkan penyebabnya: apakah tambahan pada loop
# yang memperlambat irama loop, atau sensor jarak yang salah mendeteksi
# dinding saat robot sedang mengikuti garis.
#
# Kiri dan kanan memilih tugas, tengah menjalankan, Bluetooth keluar.

from pybricks.parameters import Button
from pybricks.tools import StopWatch, wait

from perangkat import hub, robot, sensor, arm, distance_sensor

# Samakan dengan main.py.
BLACK = 9
WHITE = 85
BASE_SPEED = 150
MIN_SPEED = 60
KP = 0.8
KD = 3.0
LOOP_MS = 10
WALL_MM = 120

THRESHOLD = (BLACK + WHITE) / 2
SCALE = 200 / (WHITE - BLACK)

SECONDS = 3


def measure(label, work, seconds=SECONDS):
    """Jalankan `work` berulang selama beberapa detik, cetak irama loopnya."""
    timer = StopWatch()
    count = 0
    while timer.time() < seconds * 1000:
        work()
        count = count + 1
    rate = count / seconds
    print(label)
    print("   ", count, "siklus dalam", seconds, "detik =", rate, "siklus per detik")
    print("   ", "periode nyata", 1000 / rate, "ms, sedangkan LOOP_MS", LOOP_MS, "ms")
    return rate


def task_loop_rate():
    """Mengukur berapa lama setiap tambahan pada loop.

    Baseline yang sudah teruji cuma punya refleksi sensor di dalam loop.
    main.py sekarang menambahkan pembacaan sensor jarak setiap siklus.
    Selisih keempat angka di bawah menunjukkan berapa biaya tambahan itu.

    Loop pengikut garis mengandaikan irama yang tetap. KD adalah selisih
    error per satu siklus, jadi kalau irama loopnya berubah-ubah, KD yang
    sudah disetel ikut berubah artinya. Lihat pengikut-garis.md bagian 6
    dan bagian 11.
    """
    print("")
    print("mengukur 4 bentuk loop, masing-masing", SECONDS, "detik.")
    print("robot tidak bergerak. tidak butuh lintasan.")
    print("")

    # 1. Cuma wait. Ini batas atas yang mungkin.
    measure(
        "1. wait saja (batas atas)",
        lambda: wait(LOOP_MS),
    )

    # 2. Seperti baseline yang sudah teruji dua kali.
    measure(
        "2. sensor.reflection() saja (seperti baseline teruji)",
        lambda: (sensor.reflection(), wait(LOOP_MS)),
    )

    # 3. Seperti main.py tim sekarang.
    if distance_sensor is None:
        print("3. dilewati: sensor jarak tidak terpasang")
        print("4. dilewati: sensor jarak tidak terpasang")
    else:
        measure(
            "3. reflection() + distance() (seperti main.py tim)",
            lambda: (sensor.reflection(), distance_sensor.distance(), wait(LOOP_MS)),
        )

        # 4. Sama seperti 3, tapi motor lengan menahan posisinya.
        arm.hold()
        measure(
            "4. seperti 3, ditambah arm.hold()",
            lambda: (sensor.reflection(), distance_sensor.distance(), wait(LOOP_MS)),
        )
        arm.brake()

    print("")
    print("Cara membacanya. Kalau nomor 3 jauh lebih kecil dari nomor 2,")
    print("pembacaan sensor jaraknya yang menentukan irama loop, dan itu")
    print("penyebab pengikut garisnya jadi tidak konsisten. Jalan keluarnya")
    print("di main.py: baca sensor jarak tiap WALL_CHECK_EVERY siklus,")
    print("bukan setiap siklus.")
    print("")
    print("Kalau nomor 4 jauh lebih kecil dari nomor 3, motor lengan yang")
    print("menahan posisi terus ikut memakan waktu. Coba ARM_HOLD_WHILE")
    print("FOLLOWING = False di main.py.")


def task_wall_log():
    """Mencatat apakah sensor jarak salah mendeteksi dinding.

    Robot mengikuti garis pelan-pelan sambil mencatat jarak tiap siklus.
    Yang dicari: bacaan di bawah WALL_MM saat robot sebenarnya tidak
    sedang menghadap dinding. Kalau ada, robot akan berhenti dan
    menjalankan manuver dinding di tengah lintasan, dan dari luar itu
    terlihat seperti pengikut garis yang tiba-tiba rusak.

    Butuh lintasan. Tekan tombol tengah hub untuk berhenti.
    """
    if distance_sensor is None:
        print("sensor jarak tidak terpasang, tugas ini tidak bisa dijalankan")
        return

    print("")
    print("letakkan robot di garis. robot jalan pelan 20 detik sambil")
    print("mencatat jarak. tekan tombol tengah hub untuk berhenti.")
    print("")

    timer = StopWatch()
    last_error = 0
    lowest = 9999
    suspects = 0
    samples = 0

    while timer.time() < 20000:
        pressed = hub.buttons.pressed()
        if Button.CENTER in pressed:
            print("dihentikan")
            break

        distance = distance_sensor.distance()
        samples = samples + 1
        if distance < lowest:
            lowest = distance
        if distance < WALL_MM:
            suspects = suspects + 1
            print(
                "   MENDUGA DINDING: jarak",
                distance,
                "mm pada",
                timer.time(),
                "ms",
            )

        error = (sensor.reflection() - THRESHOLD) * SCALE
        derivative = error - last_error
        speed = BASE_SPEED - (BASE_SPEED - MIN_SPEED) * abs(error) / 100
        robot.drive(speed / 2, KP * error + KD * derivative)
        last_error = error

        wait(LOOP_MS)

    robot.stop()

    print("")
    print("selesai.")
    print("jumlah bacaan:", samples)
    print("jarak terkecil yang terlihat:", lowest, "mm")
    print("bacaan di bawah WALL_MM:", suspects)
    print("")
    if suspects == 0:
        print("Bersih. Sensor jarak tidak salah mendeteksi dinding.")
    else:
        print("Ada", suspects, "bacaan di bawah WALL_MM. Kalau robot tidak")
        print("sedang menghadap dinding saat itu, ini penyebab pengikut")
        print("garisnya terlihat rusak tiba-tiba. Naikkan WALL_READS di")
        print("main.py, atau turunkan WALL_MM.")


TASKS = (
    ("kecepatan loop", task_loop_rate),
    ("catat deteksi dinding", task_wall_log),
)


def menu():
    index = 0
    while True:
        hub.display.number(index + 1)
        pressed = hub.buttons.pressed()

        if Button.LEFT in pressed:
            index = (index - 1) % len(TASKS)
            wait(250)
        elif Button.RIGHT in pressed:
            index = (index + 1) % len(TASKS)
            wait(250)
        elif Button.CENTER in pressed:
            hub.display.off()
            name, function = TASKS[index]
            print("")
            print("=== ", name, " ===")
            function()
            print("=== selesai ===")
            robot.stop()
            wait(500)
        elif Button.BLUETOOTH in pressed:
            hub.display.off()
            break

        wait(20)


menu()
