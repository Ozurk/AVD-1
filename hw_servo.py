from adafruit_servokit import ServoKit
import time

# Initialize the I2C PCA9685 (address 0x40 is default)
# 16 channels is standard for PCA9685 breakout boards
kit = ServoKit(channels=16)

class Servo():
    def __init__(self, channel, min_angle=0, max_angle=180):
        self.channel = channel
        self.servo = kit.servo[self.channel]
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.current_angle = 0.0
        self.calibrate()

    def calibrate(self):
        self.current_angle = self.min_angle
        self.servo.angle = self.current_angle
        
        while self.current_angle <= self.max_angle:
            self.current_angle += 1
            time.sleep(0.003)
            self.servo.angle = self.current_angle
            
        while self.current_angle >= self.min_angle:
            self.current_angle -= 1
            self.servo.angle = self.current_angle
            time.sleep(0.003)

        # Correct midpoint calculation[cite: 4]
        self.current_angle = (self.max_angle + self.min_angle) / 2.0
        self.servo.angle = self.current_angle
        time.sleep(0.2)
        self.relax()  # Cut power to freeze without jitter[cite: 4]

    def move(self, distance):
        """Move the servo by a certain distance."""
        old_angle = self.current_angle
        
        # Map the arbitrary 'distance' to an angle change (approx 0.36 degrees per unit 
        # to match the old duty cycle scaling of distance/100 over a 5.0 duty range)[cite: 4]
        angle_change = distance * 0.36
        new_angle = self.current_angle + angle_change

        if self.min_angle <= new_angle <= self.max_angle:
            self.current_angle = new_angle
            self.servo.angle = self.current_angle
        else:
            self.current_angle = old_angle  # Revert to old angle if out of bounds[cite: 4]

    def relax(self):
        """Set angle to None to completely shut off the PWM signal when idle."""
        self.servo.angle = None