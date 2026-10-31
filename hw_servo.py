import time
from adafruit_servokit import ServoKit

# Initialize the PCA9685 board on standard I2C address 0x40
kit = ServoKit(channels=16)

class Servo:
    def __init__(self, channel: int):
        self.channel = channel
        self.servo = kit.servo[self.channel]
        
        # PCA9685 uses 0 to 180 degrees; 90.0 is center
        self.current_angle = 90.0 
        self.calibrate()

    def calibrate(self):
        """Smoothly sweep the servo limits on boot to prevent power brown-outs."""
        self.current_angle = 90.0
        
        # Sweep to min (0 degrees)
        while self.current_angle > 0.0:
            self.current_angle = max(0.0, self.current_angle - 1.0)
            self.servo.angle = self.current_angle
            time.sleep(0.01)
            
        # Sweep to max (180 degrees)
        while self.current_angle < 180.0:
            self.current_angle = min(180.0, self.current_angle + 1.0)
            self.servo.angle = self.current_angle
            time.sleep(0.01)
            
        # Back to center (90 degrees)
        while self.current_angle > 90.0:
            self.current_angle = max(90.0, self.current_angle - 1.0)
            self.servo.angle = self.current_angle
            time.sleep(0.01)

        self.current_angle = 90.0
        self.servo.angle = self.current_angle
        time.sleep(0.2)
        self.relax()

    def move(self, distance: float):
        """Move the servo proportionally to the pixel error distance."""
        # Convert the prior relative pixel mapping into degree shifts.
        # Original math: (distance / 100.0) * (2.0 / 5.0). 
        # Scaled to a 180-degree system, this maps to approx: distance * 0.36
        angle_shift = distance * 0.36
        new_angle = self.current_angle + angle_shift

        # Clamp safely within physical limits
        if 0.0 <= new_angle <= 180.0:
            self.current_angle = new_angle
            self.servo.angle = self.current_angle
        else:
            # Snap to limit if target exceeds bounds
            self.current_angle = 180.0 if new_angle > 180.0 else 0.0
            self.servo.angle = self.current_angle
            
    def relax(self):
        """Turn off the active PWM signal to completely eliminate electrical jitter."""
        self.servo.angle = None