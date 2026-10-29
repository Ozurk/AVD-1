import os
import time

# Force gpiozero to use the native Pi 5 lgpio driver for hardware-timed PWM
os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"
from gpiozero import Servo as GZServo

class Servo:
    def __init__(self, pin: int, frequency: int = 50, min_duty: float = 5.0, max_duty: float = 10.0):
        # Convert duty cycle percentages back to pulse widths in seconds for gpiozero
        period = 1.0 / frequency
        min_pulse = (min_duty / 100.0) * period
        max_pulse = (max_duty / 100.0) * period
        
        # Initialize the servo on the given physical GPIO pin
        self.servo = GZServo(pin, min_pulse_width=min_pulse, max_pulse_width=max_pulse)
        self.min_duty = min_duty
        self.max_duty = max_duty
        
        # gpiozero tracks position using a scale from -1.0 (min) to 1.0 (max), 0.0 is center
        self.current_value = 0.0 
        self.calibrate()

    def calibrate(self):
        """Smoothly sweep the servo limits on boot to prevent power brown-outs."""
        self.current_value = 0.0
        
        # Sweep to min
        while self.current_value > -1.0:
            self.current_value = max(-1.0, self.current_value - 0.05)
            self.servo.value = self.current_value
            time.sleep(0.01)
            
        # Sweep to max
        while self.current_value < 1.0:
            self.current_value = min(1.0, self.current_value + 0.05)
            self.servo.value = self.current_value
            time.sleep(0.01)
            
        # Back to center
        while self.current_value > 0.0:
            self.current_value = max(0.0, self.current_value - 0.05)
            self.servo.value = self.current_value
            time.sleep(0.01)

        self.current_value = 0.0
        self.servo.value = self.current_value
        time.sleep(0.2)
        self.relax()

    def move(self, distance: float):
        """Move the servo proportionally to the pixel error distance."""
        # Convert the raw pixel distance into gpiozero's -1.0 to 1.0 scale
        duty_range = self.max_duty - self.min_duty
        scale_factor = 2.0 / duty_range
        
        # We divide by 100.0 to match the scaling of your original duty cycle math
        value_shift = (distance / 100.0) * scale_factor
        new_value = self.current_value + value_shift

        # Clamp safely within physical limits
        if -1.0 <= new_value <= 1.0:
            self.current_value = new_value
            self.servo.value = self.current_value
        else:
            # Snap to limit if target exceeds bounds
            self.current_value = 1.0 if new_value > 1.0 else -1.0
            self.servo.value = self.current_value
            
    def relax(self):
        """Turn off the active PWM signal to completely eliminate electrical jitter."""
        self.servo.value = None