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
        self.calibrate()  # Calibrate the servo on initialization

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

        self.current_duty = self.max_duty - self.min_duty / 2
        self.pwm.change_duty_cycle(self.current_duty)

    def move(self, distance):
        """
        move the servio by a certain distance. Positive values move it one way, negative values the other.
        """
        old_duty = self.current_duty
        new_duty = self.current_duty + distance / 100

        if self.min_duty <= new_duty <= self.max_duty:
            self.current_duty = new_duty
            self.pwm.change_duty_cycle(self.current_duty)
        else:
            print(f"Attempted to move servo to {new_duty}, which is out of bounds ({self.min_duty}-{self.max_duty}).")
            self.current_duty = old_duty  # Revert to old duty cycle if out of bounds


          