from rpi_hardware_pwm import HardwarePWM
import time

class Servo():
    def __init__(self, channel, frequency=50, min_duty=5.0, max_duty=10.0):
        # rpi_hardware_pwm uses chip=0 by default, which is correct for Pi 5 GPIO header
        self.pwm = HardwarePWM(pwm_channel=channel, hz=frequency)
        self.pwm.start(0)  # Start with 0% duty cycle
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.current_duty = 0.0
        self.calibrate()

    def calibrate(self):
        self.current_duty = self.min_duty
        self.pwm.change_duty_cycle(self.current_duty)
        
        while self.current_duty <= self.max_duty:
            self.current_duty += .01
            time.sleep(0.003)
            self.pwm.change_duty_cycle(self.current_duty)
            
        while self.current_duty >= self.min_duty:
            self.current_duty -= .01
            self.pwm.change_duty_cycle(self.current_duty)
            time.sleep(0.003)

        # FIXED: Correct midpoint calculation
        self.current_duty = (self.max_duty + self.min_duty) / 2.0
        self.pwm.change_duty_cycle(self.current_duty)
        time.sleep(0.2)
        self.relax()  # Cut power to freeze without jitter

    def move(self, distance):
        """Move the servo by a certain distance."""
        old_duty = self.current_duty
        new_duty = self.current_duty + (distance / 100.0)

        if self.min_duty <= new_duty <= self.max_duty:
            self.current_duty = new_duty
            self.pwm.change_duty_cycle(self.current_duty)
        else:
            self.current_duty = old_duty  # Revert to old duty cycle if out of bounds

    def relax(self):
        """Set duty cycle to 0 to completely shut off the PWM signal when idle."""
        self.pwm.change_duty_cycle(0)