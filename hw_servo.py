import time
from gpiozero import Servo as GZServo

class Servo:
    def __init__(self, pin: int, frequency: int = 50, min_duty: float = 5.0, max_duty: float = 10.0):
        # Convert your duty cycle percentages back to pulse widths in seconds
        period = 1.0 / frequency
        min_pulse = (min_duty / 100.0) * period
        max_pulse = (max_duty / 100.0) * period
        
        # Initialize the servo on the given GPIO pin
        self.servo = GZServo(pin, min_pulse_width=min_pulse, max_pulse_width=max_pulse)
        
        self.min_duty = min_duty
        self.max_duty = max_duty
        
        # gpiozero tracks position using a scale from -1.0 (min) to 1.0 (max), with 0.0 as center
        self.current_value = 0.0 
        self.calibrate()

    def calibrate(self):
        # Sweep from min to max
        self.current_value = -1.0
        self.servo.value = self.current_value
        while self.current_value < 1.0:
            self.current_value = min(1.0, self.current_value + 0.02)
            self.servo.value = self.current_value
            time.sleep(0.003)
            
        # Sweep from max to min
        while self.current_value > -1.0:
            self.current_value = max(-1.0, self.current_value - 0.02)
            self.servo.value = self.current_value
            time.sleep(0.003)
            
        # Center the servo
        self.current_value = 0.0
        self.servo.value = self.current_value

    def move(self, distance: float):
        """Move the servo by a certain distance."""
        old_value = self.current_value
        
        # Convert your original duty cycle shift into gpiozero's -1.0 to 1.0 scale
        duty_range = self.max_duty - self.min_duty
        scale_factor = 2.0 / duty_range
        value_shift = (distance / 100.0) * scale_factor
        
        new_value = self.current_value + value_shift

        if -1.0 <= new_value <= 1.0:
            self.current_value = new_value
            self.servo.value = self.current_value
        else:
            print("Attempted to move servo out of bounds.")
            self.current_value = old_value
            
    def stop(self):
        # Setting value to None stops sending the PWM signal
        self.servo.value = None