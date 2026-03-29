import RPi.GPIO as GPIO
from config import L_PWM_FWD, L_PWM_REV, R_PWM_FWD, R_PWM_REV, EN_PINS

class MotorController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in EN_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
        for pin in [L_PWM_FWD, L_PWM_REV, R_PWM_FWD, R_PWM_REV]:
            GPIO.setup(pin, GPIO.OUT)
        self.l_fwd = GPIO.PWM(L_PWM_FWD, 1000); self.l_fwd.start(0)
        self.l_rev = GPIO.PWM(L_PWM_REV, 1000); self.l_rev.start(0)
        self.r_fwd = GPIO.PWM(R_PWM_FWD, 1000); self.r_fwd.start(0)
        self.r_rev = GPIO.PWM(R_PWM_REV, 1000); self.r_rev.start(0)

    def kontrol(self, sol, sag):
        if sol > 0:
            self.l_fwd.ChangeDutyCycle(sol)
            self.l_rev.ChangeDutyCycle(0)
        elif sol < 0:
            self.l_fwd.ChangeDutyCycle(0)
            self.l_rev.ChangeDutyCycle(abs(sol))
        else:
            self.l_fwd.ChangeDutyCycle(0)
            self.l_rev.ChangeDutyCycle(0)
        
        if sag > 0:
            self.r_fwd.ChangeDutyCycle(sag)
            self.r_rev.ChangeDutyCycle(0)
        elif sag < 0:
            self.r_fwd.ChangeDutyCycle(0)
            self.r_rev.ChangeDutyCycle(abs(sag))
        else:
            self.r_fwd.ChangeDutyCycle(0)
            self.r_rev.ChangeDutyCycle(0)

    def stop(self):
        self.kontrol(0, 0)

    def cleanup(self):
        self.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    print("MotorController test ediliyor...")
    motors = MotorController()
    motors.kontrol(50, 50)
    import time
    time.sleep(2)
    motors.stop()
    print("Test tamamlandı.")