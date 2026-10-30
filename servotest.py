from hw_servo import Servo
import time

def test_servo_sweep():
    # GPIO 18 corresponds to hardware PWM channel 0 on Raspberry Pi.
    print("Initializing Servo on GPIO 18 (Channel 0)...")
    
    # The __init__ method automatically calls calibrate(), which performs an initial sweep[cite: 2].
    servo = Servo(channel=0)
    time.sleep(1) 

    # Manually move to the starting position (minimum duty cycle)
    print("Moving to minimum position...")
    servo.current_duty = servo.min_duty
    servo.pwm.change_duty_cycle(servo.current_duty)
    time.sleep(0.5)

    print("Sweeping full range of motion over 2 seconds...")
    steps = 100
    sleep_time = 2.0 / steps
    # Calculate how much to increase the duty cycle per step based on min and max[cite: 2]
    step_increase = (servo.max_duty - servo.min_duty) / steps 

    # Execute the 2-second sweep
    for _ in range(steps):
        servo.current_duty += step_increase
        servo.pwm.change_duty_cycle(servo.current_duty)
        time.sleep(sleep_time)

    print("Sweep complete. Relaxing servo.")
    # Cut power to the servo to prevent jittering when idle[cite: 2]
    servo.relax()

if __name__ == "__main__":
    test_servo_sweep()