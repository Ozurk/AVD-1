from rpi_hardware_pwm import HardwarePWM
import time

# Initialize PWM Channel 0 (GPIO 18) at 50Hz (standard servo frequency)
pwm = HardwarePWM(pwm_channel=0, hz=50)
pwm.start(0) # Start with 0% duty cycle

try:
    # Standard servos operate between 5% and 10% duty cycle at 50Hz
    print("Moving to 0 degrees")
    pwm.change_duty_cycle(5.0)  # ~1ms pulse
    time.sleep(1)

    print("Moving to 90 degrees (center)")
    pwm.change_duty_cycle(7.5)  # ~1.5ms pulse
    time.sleep(1)

    print("Moving to 180 degrees")
    # pwm.change_duty_cycle(10.0) # ~2.0ms pulse
    time.sleep(1)


    # Initialize PWM Channel 1 (GPIO 18) at 50Hz (standard servo frequency)
    pwm = HardwarePWM(pwm_channel=1, hz=50)
    pwm.start(1) # Start with 0% duty cycle


    # Standard servos operate between 5% and 10% duty cycle at 50Hz
    print("Moving to 0 degrees")
    pwm.change_duty_cycle(5.0)  # ~1ms pulse
    time.sleep(1)

    print("Moving to 90 degrees (center)")
    pwm.change_duty_cycle(7.5)  # ~1.5ms pulse
    time.sleep(1)

    print("Moving to 180 degrees")
    pwm.change_duty_cycle(10.0) # ~2.0ms pulse
    time.sleep(1)

finally:
    pwm.stop()