# Menguji pengangkat sensor, sensor jarak, dan pembacaan warna dinding.
# Mulai dengan sensor warna menghadap bawah. Program mengangkat sensor ke depan,
# lalu mencetak jarak dan warna terus-menerus. Dekatkan dinding tiap warna,
# catat jarak saat warnanya mulai terbaca benar, dan pakai untuk READ_MM di main.py.
# Tekan tombol kiri hub untuk menurunkan sensor dan selesai.

from pybricks.parameters import Button, Color
from pybricks.tools import wait

from perangkat import hub, arm, sensor, distance_sensor

# Samakan dengan ARM_UP_DEG dan ARM_SPEED di main.py.
ARM_UP_DEG = 90
ARM_SPEED = 300

if distance_sensor is None:
    print("Sensor jarak tidak ditemukan. Periksa port di perangkat.py.")

sensor.detectable_colors(
    [Color.RED, Color.GREEN, Color.YELLOW, Color.WHITE, Color.BLACK, Color.NONE]
)
arm.run_target(ARM_SPEED, ARM_UP_DEG)

while Button.LEFT not in hub.buttons.pressed():
    jarak = distance_sensor.distance() if distance_sensor is not None else "-"
    print("jarak =", jarak, "mm  warna =", sensor.color(), " hsv =", sensor.hsv())
    wait(200)

arm.run_target(ARM_SPEED, 0)
