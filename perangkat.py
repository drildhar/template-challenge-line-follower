# Blok setup robot. Dipakai bersama oleh main.py dan kalibrasi.py,
# jadi port dan ukuran roda cukup diubah di satu tempat ini.

from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Direction
from pybricks.robotics import DriveBase

hub = InventorHub()
left = Motor(Port.E, Direction.COUNTERCLOCKWISE)
right = Motor(Port.F, Direction.CLOCKWISE)
sensor = ColorSensor(Port.D)

# Ganti dengan hasil kalibrasi robot kalian sendiri,
# lihat bagian 8 dasar-pybricks.md.
robot = DriveBase(left, right, wheel_diameter=56, axle_track=114)

# Motor pengangkat sensor warna. Sudut 0 = sensor menghadap bawah,
# jadi pastikan sensor menghadap bawah setiap kali program dimulai.
arm = Motor(Port.A)
arm.reset_angle(0)

# Sensor jarak menghadap ke depan untuk mendeteksi dinding.
# Kalau belum terpasang, nilainya None dan main.py tetap jalan
# sebagai pengikut garis biasa.
try:
    distance_sensor = UltrasonicSensor(Port.C)
except OSError:
    distance_sensor = None
