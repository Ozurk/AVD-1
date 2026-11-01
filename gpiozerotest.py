import time
from adafruit_servokit import ServoKit

# Initialize the I2C PWM/Servo driver (e.g., PCA9685).
# Note: The typical default I2C address for the PCA9685 is 0x40.
# We are setting address=0x00 as requested.
kit = ServoKit(channels=16, address=0x00)

# Assuming the servo is attached to channel 0
servo = kit.servo[0]

def sweep_servo():
    print("Starting servo sweep. Press Ctrl+C to stop.")
    try:
        while True:
            # Sweep from 0 to 180 degrees
            for angle in range(0, 181, 1):
                servo.angle = angle
                time.sleep(0.015)
            
            # Sweep from 180 down to 0 degrees
            for angle in range(180, -1, -1):
                servo.angle = angle
                time.sleep(0.015)
                
    except KeyboardInterrupt:
        print("\nSweep stopped.")
        # Optional: return servo to 0 or 90 degrees when stopped
        # servo.angle = 0

if __name__ == '__main__':
    sweep_servo()