from rpi_hardware_pwm import HardwarePWM
import time

# Initialize Channel 0 (GPIO 18) and Channel 1 (GPIO 19) at 50Hz
class Servo():
    def __init__(self, channel, frequency=50, min_duty=5, max_duty=10):
        self.pwm = HardwarePWM(channel=channel, frequency=frequency)
        self.pwm.start(0)  # Start with 0% duty cycle
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.current_duty = 0  # Track the current duty cycle

    def calibrate(self):
        self.current_duty = self.min_duty

        self.pwm.change_duty_cycle(self.current_duty)
        while self.current_duty <= self.max_duty:
            self.current_duty += .001
            self.pwm.change_duty_cycle(self.current_duty)
        while self.current_duty >= self.min_duty:
            self.current_duty -= .001
            self.pwm.change_duty_cycle(self.current_duty)

vert = Servo(1)

vert.calibrate()
        

          