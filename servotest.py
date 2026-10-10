import gpiozero
import time

servo = gpiozero.Servo(18)

servo.min()  # Move the servo to its minimum position
time.sleep(1)  # Wait for 1 second
servo.mid()  # Move the servo to its middle position
time.sleep(1)  # Wait for 1 second
servo.max()  # Move the servo to its maximum position