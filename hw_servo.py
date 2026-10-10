from rpi_hardware_pwm import HardwarePWM
import time

# Initialize Channel 0 (GPIO 18) and Channel 1 (GPIO 19) at 50Hz
servo_18 = HardwarePWM(pwm_channel=0, hz=50)
servo_19 = HardwarePWM(pwm_channel=1, hz=50)

# Start both with a 0% duty cycle (off)
servo_18.start(0)
servo_19.start(0)

try:
    print("Moving both to 0 degrees")
    servo_18.change_duty_cycle(5.0)
    servo_19.change_duty_cycle(5.0)
    time.sleep(1.5)

    print("Moving in opposite directions")
    servo_18.change_duty_cycle(7.5) 
    servo_19.change_duty_cycle(7.5)  # Stay at 0 degrees
    time.sleep(1.5)

    print("Moving both to center (90 degrees)")
    servo_18.change_duty_cycle(5.5)
    servo_19.change_duty_cycle(10)
    time.sleep(1.5)

finally:
    # Always stop the PWM signals cleanly before exiting
    servo_18.stop()
    servo_19.stop()