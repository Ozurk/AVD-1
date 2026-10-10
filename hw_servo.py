from rpi_hardware_pwm import HardwarePWM
import time

# Initialize Channel 0 (GPIO 18) and Channel 1 (GPIO 19) at 50Hz
class Servo():
    def __init__(self, channel, frequency=50, min_duty=5, max_duty=10):
        self.pwm = HardwarePWM(pwm_channel=channel, hz=frequency)
        self.pwm.start(0)  # Start with 0% duty cycle
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.current_duty = 0  # Track the current duty cycle

    def calibrate(self):
        self.current_duty = self.min_duty

        self.pwm.change_duty_cycle(self.current_duty)
        while self.current_duty <= self.max_duty:
            self.current_duty += .01
            time.sleep(0.003)  # Small delay to allow the servo to move
            self.pwm.change_duty_cycle(self.current_duty)
        while self.current_duty >= self.min_duty:
            self.current_duty -= .01
            self.pwm.change_duty_cycle(self.current_duty)
            time.sleep(0.003)  # Small delay to allow the servo to move

vert = Servo(0, frequency=50, min_duty=5, max_duty=8)
horiz = Servo(1, frequency=50, min_duty=5, max_duty=10)

vert.calibrate()
horiz.calibrate()

          