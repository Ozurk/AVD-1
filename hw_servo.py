import time
from rpi_hardware_pwm import HardwarePWM


class Servo:

  def __init__(
      self,
      channel: int,
      frequency: int = 50,
      min_duty: float = 5.0,
      max_duty: float = 10.0,
      chip: int = 2,
  ):
    # On RPi 5:
    # Use channel 2 for GPIO 18, channel 3 for GPIO 19
    # Verify the chip number using `ls /sys/class/pwm/` (commonly chip=2 or chip=0)
    self.pwm = HardwarePWM(pwm_channel=channel, hz=frequency, chip=chip)
    self.pwm.start(0)  # Start with 0% duty cycle
    self.min_duty = min_duty
    self.max_duty = max_duty
    self.current_duty = 0.0
    self.calibrate()

  def calibrate(self):
    self.current_duty = self.min_duty
    self.pwm.change_duty_cycle(self.current_duty)

    # Sweep min to max
    while self.current_duty <= self.max_duty:
      self.current_duty += 0.01
      time.sleep(0.003)
      self.pwm.change_duty_cycle(self.current_duty)

    # Sweep max to min
    while self.current_duty >= self.min_duty:
      self.current_duty -= 0.01
      time.sleep(0.003)
      self.pwm.change_duty_cycle(self.current_duty)

    # Move to center midpoint
    self.current_duty = (self.min_duty + self.max_duty) / 2
    self.pwm.change_duty_cycle(self.current_duty)

  def move(self, distance: float):
    """Move the servo by a certain distance relative to current duty cycle."""
    old_duty = self.current_duty
    new_duty = self.current_duty + (distance / 100.0)

    if self.min_duty <= new_duty <= self.max_duty:
      self.current_duty = new_duty
      self.pwm.change_duty_cycle(self.current_duty)
    else:
      print(
          f"Attempted to move servo to {new_duty:.2f}, "
          f"which is out of bounds ({self.min_duty}-{self.max_duty})."
      )
      self.current_duty = old_duty

  def stop(self):
    self.pwm.stop()


# Example usage on Raspberry Pi 5 for GPIO 18:
# servo_18 = Servo(channel=2, chip=2)