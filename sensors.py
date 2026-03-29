import serial
import time

try:
    from rplidar import RPLidar
except ImportError:
    RPLidar = None

try:
    import board
    import busio
    import adafruit_bmp280
except ImportError:
    board = busio = adafruit_bmp280 = None

from config import SERIAL_PORT, LIDAR_PORT

class SensorManager:
    def __init__(self):
        self.bmp_sensor = None
        self.old_pressure = 1013.25
        if board and busio and adafruit_bmp280:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.bmp_sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
                self.old_pressure = self.bmp_sensor.pressure
            except:
                self.bmp_sensor = None

        self.ser = None
        try:
            self.ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
        except:
            pass

        self.lidar = None
        if RPLidar:
            try:
                self.lidar = RPLidar(LIDAR_PORT)
                self.lidar.connect()
            except:
                self.lidar = None

    def get_sensor_data(self):
        sensor_data = ""
        if self.bmp_sensor:
            current = self.bmp_sensor.pressure
            force = abs(current - self.old_pressure) * 10
            self.old_pressure = current
            sensor_data = f"| P:{current:.2f} | T:{self.bmp_sensor.temperature:.2f} | F:{force:.2f}"
        return sensor_data

    def read_gps_line(self):
        if self.ser and self.ser.in_waiting > 0:
            return self.ser.readline().decode('utf-8', errors='ignore').strip()
        return None

    def obstacle_detected(self):
        if not self.lidar:
            return False
        try:
            for scan in self.lidar.iter_scans():
                for (_, angle, distance) in scan:
                    if (angle < 45 or angle > 315) and 0 < distance < 500:
                        return True
                break
        except:
            return False
        return False

    def cleanup(self):
        if self.lidar:
            self.lidar.stop()
            self.lidar.disconnect()
        if self.ser:
            self.ser.close()

if __name__ == "__main__":
    print("SensorManager test ediliyor...")
    sensors = SensorManager()
    print(f"BMP280: {'Var' if sensors.bmp_sensor else 'Yok'}")
    print(f"LIDAR: {'Var' if sensors.lidar else 'Yok'}")
    print("Sensor data örnek:", sensors.get_sensor_data())