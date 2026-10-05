# Pengikut garis PD dengan kecepatan adaptif, pencarian garis hilang,
# dan manuver di depan dinding berwarna. Sensor warna diangkat ke depan
# oleh motor A untuk membaca warna dinding, lalu diturunkan lagi.
# Penjelasan pengikut garis ada di pengikut-garis.md.

from pybricks.parameters import Button, Color
from pybricks.tools import wait, StopWatch

from perangkat import hub, robot, sensor, arm, distance_sensor

# --- hasil pengukuran, ukur ulang dengan kalibrasi.py setiap ganti lintasan atau ruangan ---
BLACK = 9
WHITE = 85

# --- setelan pengikut garis, setel satu per satu ---
BASE_SPEED = 150
MIN_SPEED = 60
KP = 0.8
KD = 3.0
LOOP_MS = 10
LOST_MS = 300

# --- setelan pengangkat sensor ---
ARM_UP_DEG = 90           # sudut motor A saat sensor menghadap depan (balik tandanya kalau arahnya salah)
ARM_SPEED = 300           # kecepatan motor A, derajat per detik
# Motor lengan menahan posisinya terus selama robot mengikuti garis. Itu
# menjaga tinggi sensor tetap sama supaya BLACK dan WHITE tidak bergeser,
# tapi motor itu terus bekerja. Setel False kalau diagnosa.py menunjukkan
# motor lengan ikut memperlambat loop.
ARM_HOLD_WHILE_FOLLOWING = True

# --- setelan dinding, ukur dengan kalibrasi_dinding.py ---
WALL_MM = 120             # dinding dianggap ada kalau jaraknya di bawah ini
WALL_READS = 3            # jumlah bacaan berturut-turut sebelum robot percaya ada dinding
WALL_CHECK_EVERY = 5      # periksa sensor jarak tiap sekian siklus, BUKAN tiap siklus
WALL_COOLDOWN_MS = 2000   # abaikan dinding sebentar setelah manuver
READ_MM = 50              # dekati dinding sampai jarak ini sebelum membaca warna
APPROACH_SPEED = 60       # kecepatan mendekati dinding, mm per detik
APPROACH_MAX_MM = 100     # paling jauh maju mendekati dinding, supaya tidak menabrak
COLOR_SAMPLES = 9         # jumlah bacaan warna, diambil yang paling sering
WALL_ATTEMPTS = 3         # jumlah percobaan membaca warna sebelum menyerah
NUDGE_MM = 15             # maju sekian mm di antara percobaan
FORWARD_MM = 40           # maju setelah baca warna supaya roda tepat di persimpangan
TURN_FIRST_DEG = 45       # putar dulu tanpa melihat sensor, supaya lepas dari garis lama
SEARCH_DEG = 120          # paling jauh berputar saat mencari garis di satu sisi
TURN_SPEED = 120          # kecepatan putar saat mencari garis, derajat per detik
SEARCH_TIMEOUT_MS = 3000  # batas waktu mencari garis, supaya loop tidak menggantung

# --- batas keselamatan ---
# Juri memberi batas 10 menit. Berhenti sendiri satu menit lebih awal supaya
# robot tidak terus berjalan setelah waktunya habis.
MAX_RUNTIME_MS = 9 * 60 * 1000

LEFT = -1
RIGHT = 1
YELLOW_TURN = RIGHT       # kuning boleh kiri atau kanan, pilihan tim
FALLBACK_TURN = RIGHT     # dipakai kalau warna tidak terbaca

THRESHOLD = (BLACK + WHITE) / 2
SCALE = 200 / (WHITE - BLACK)
WALL_COLORS = (Color.RED, Color.GREEN, Color.YELLOW)

# Batasi pilihan warna supaya karton atau bayangan tidak terbaca sebagai warna lain.
# Ini hanya memengaruhi color(), reflection() untuk garis tetap sama.
sensor.detectable_colors(
    [Color.RED, Color.GREEN, Color.YELLOW, Color.WHITE, Color.BLACK, Color.NONE]
)


def read_wall_color():
    # Baca beberapa kali lalu ambil warna yang paling sering muncul,
    # supaya satu bacaan meleset tidak membuat robot salah belok.
    counts = [0, 0, 0]
    for i in range(COLOR_SAMPLES):
        color = sensor.color()
        for k in range(3):
            if color == WALL_COLORS[k]:
                counts[k] += 1
        wait(20)
    best = max(range(3), key=lambda k: counts[k])
    if counts[best] * 2 > COLOR_SAMPLES:
        return WALL_COLORS[best]
    return None


def read_wall():
    # Angkat sensor, dekati dinding, baca warna, lalu kembali ke posisi
    # semula dan turunkan sensor supaya bisa melihat garis lagi.
    arm.run_target(ARM_SPEED, ARM_UP_DEG)

    start = robot.distance()
    robot.drive(APPROACH_SPEED, 0)
    while distance_sensor.distance() > READ_MM and robot.distance() - start < APPROACH_MAX_MM:
        wait(10)
    robot.stop()

    color = read_wall_color()

    # Dinding yang menyudut atau kena bayangan sering belum terbaca pada
    # percobaan pertama. Maju sedikit lagi dan coba ulang, tapi tetap
    # dibatasi APPROACH_MAX_MM supaya tidak menabrak dindingnya.
    for attempt in range(WALL_ATTEMPTS - 1):
        if color is not None:
            break
        if robot.distance() - start >= APPROACH_MAX_MM:
            print("warna belum terbaca dan sudah tidak bisa maju lagi")
            break
        print("warna belum terbaca, maju", NUDGE_MM, "mm lagi")
        robot.straight(NUDGE_MM)
        color = read_wall_color()

    robot.straight(start - robot.distance())
    arm.run_target(ARM_SPEED, 0)
    return color


def turn_for(color):
    if color == Color.RED:
        return LEFT
    if color == Color.GREEN:
        return RIGHT
    if color == Color.YELLOW:
        return YELLOW_TURN
    return FALLBACK_TURN


def turn_to_line(direction):
    # Putar ke satu sisi sampai sensor bawah menemukan garis.
    # Mengembalikan True kalau garis ketemu, False kalau tidak.
    start = robot.angle()
    robot.turn(direction * TURN_FIRST_DEG)

    timer = StopWatch()
    robot.drive(0, direction * TURN_SPEED)
    found = False
    while abs(robot.angle() - start) < SEARCH_DEG:
        if sensor.reflection() < THRESHOLD:
            found = True
            break
        # Tanpa batas waktu, loop ini berputar selamanya kalau roda
        # tertahan dan sudutnya tidak bertambah.
        if timer.time() > SEARCH_TIMEOUT_MS:
            print("mencari garis: waktu habis, roda mungkin tertahan")
            break
        wait(5)

    # Pengikut garis ini menempel di satu tepi garis (KP positif: tepi kiri).
    # Kalau putarannya mendekati garis dari tepi yang salah,
    # sensor harus menyeberangi garis dulu sampai ke tepi yang benar.
    if found and (direction == LEFT) == (KP > 0):
        timer.reset()
        while sensor.reflection() < THRESHOLD and abs(robot.angle() - start) < SEARCH_DEG:
            if timer.time() > SEARCH_TIMEOUT_MS:
                print("menyeberangi garis: waktu habis")
                break
            wait(5)

    robot.stop()
    return found


def wall_maneuver():
    robot.stop()
    color = read_wall()
    direction = turn_for(color)
    print("dinding:", color, "-> belok", "kanan" if direction == RIGHT else "kiri")
    hub.light.on(color if color is not None else Color.ORANGE)

    robot.straight(FORWARD_MM)
    heading = robot.angle()
    if not turn_to_line(direction):
        # Garis tidak ada di sisi itu: kembali menghadap depan, cek sisi lain.
        print("dinding: garis tidak ketemu, cek sisi lain")
        robot.turn(heading - robot.angle())
        if not turn_to_line(-direction):
            robot.turn(heading - robot.angle())

    hub.light.off()


if ARM_HOLD_WHILE_FOLLOWING:
    arm.hold()
else:
    arm.brake()

last_error = 0
lost_time = 0
wall_count = 0
loop_count = 0
timer = StopWatch()
next_wall_time = 0

while True:
    # Tombol tengah menghentikan program, dan batas waktu menghentikannya
    # sendiri sebelum batas 10 menit juri lewat.
    if Button.CENTER in hub.buttons.pressed():
        print("dihentikan manual")
        break
    if timer.time() > MAX_RUNTIME_MS:
        print("batas waktu habis, berhenti")
        break

    # Membaca sensor jarak memblokir loop. Kalau dibaca setiap siklus, irama
    # loop tidak lagi LOOP_MS dan nilai KD yang sudah disetel jadi salah.
    # Jadi diperiksa tiap WALL_CHECK_EVERY siklus saja. Ukur sendiri
    # bedanya dengan diagnosa.py tugas 1.
    if distance_sensor is not None and timer.time() >= next_wall_time:
        loop_count = loop_count + 1
        if loop_count >= WALL_CHECK_EVERY:
            loop_count = 0

            if distance_sensor.distance() < WALL_MM:
                wall_count = wall_count + 1
            else:
                wall_count = 0

            if wall_count >= WALL_READS:
                wall_maneuver()
                wall_count = 0
                loop_count = 0
                last_error = 0
                lost_time = 0
                next_wall_time = timer.time() + WALL_COOLDOWN_MS
                continue

    error = (sensor.reflection() - THRESHOLD) * SCALE

    if error > 80:
        lost_time = lost_time + LOOP_MS
    else:
        lost_time = 0

    if lost_time > LOST_MS:
        # Garis hilang: berputar ke arah garis terakhir terlihat.
        robot.drive(0, 90 if last_error > 0 else -90)
    else:
        derivative = error - last_error
        speed = BASE_SPEED - (BASE_SPEED - MIN_SPEED) * abs(error) / 100
        robot.drive(speed, KP * error + KD * derivative)
        last_error = error

    wait(LOOP_MS)

robot.stop()
hub.light.off()
print("program berhenti")
