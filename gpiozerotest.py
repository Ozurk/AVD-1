from gpiozero import Servo
from time import sleep

def test_gpiozero_sweep():
    # Initialize the servo on GPIO 18.
    # Note: Standard servos use 1ms to 2ms pulses. If your servo has a wider range 
    # (like 0.5ms to 2.5ms), initialize it like: Servo(18, min_pulse_width=0.0005, max_pulse_width=0.0025)
    servo = Servo(18)

    print("Moving to minimum position...")
    servo.min()
    sleep(1)

    print("Moving to center position...")
    servo.mid()
    sleep(1)

    print("Moving to maximum position...")
    servo.max()
    sleep(1)

    print("Starting smooth sweep...")
    
    # gpiozero maps the servo range from -1.0 (min) to 1.0 (max)
    step = 0.02
    delay = 0.02

    # Sweep from min to max
    value = -1.0
    while value <= 1.0:
        servo.value = round(value, 2)
        sleep(delay)
        value += step

    # Sweep from max back to min
    value = 1.0
    while value >= -1.0:
        servo.value = round(value, 2)
        sleep(delay)
        value -= step

    print("Sweep complete. Relaxing servo.")
    # Setting the value to None stops the PWM signal, preventing jitter
    servo.value = None

if __name__ == "__main__":
    test_gpiozero_sweep()