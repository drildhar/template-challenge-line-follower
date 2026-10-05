# Mengukur BLACK dan WHITE secara otomatis.
# Letakkan robot dengan sensor tepat di atas garis, lalu jalankan.
# Robot berputar di tempat selama 5 detik dan menyapu garis beberapa kali.
# Salin angka yang tercetak ke BLACK dan WHITE di main.py.

from pybricks.tools import wait, StopWatch

from perangkat import robot, sensor

timer = StopWatch()
lo = 100
hi = 0

robot.drive(0, 60)

while timer.time() < 5000:
    value = sensor.reflection()
    lo = min(lo, value)
    hi = max(hi, value)
    wait(10)

robot.stop()

print("BLACK =", lo)
print("WHITE =", hi)
if hi - lo < 30:
    print("Selisih kurang dari 30. Turunkan sensor atau periksa kontras lintasan.")
