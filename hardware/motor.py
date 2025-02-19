import RPi.GPIO as gpio
from typing import Tuple


class Motor:
    """
    Controls a DC motor using PWM via the Raspberry Pi GPIO.

    Supports forward, backward, and stop operations with speed control.
    """

    def __init__(self, motor_pins: Tuple[int, int, int]) -> None:
        """
        Initializes the motor and sets up the GPIO pins.

        Args:
            motor_pins (Tuple[int, int, int]): Tuple containing the GPIO pin numbers (enable, in1, in2).
        """
        # Assign pin numbers
        self.enable: int = motor_pins[0]  # PWM enable pin
        self.in1: int = motor_pins[1]  # Direction control pin 1
        self.in2: int = motor_pins[2]  # Direction control pin 2

        # Set up GPIO
        gpio.setmode(gpio.BCM)  # Use Broadcom pin numbering
        gpio.setup(self.in1, gpio.OUT)
        gpio.setup(self.in2, gpio.OUT)
        gpio.setup(self.enable, gpio.OUT)

        # Default motor state: stopped
        gpio.output(self.in1, gpio.LOW)
        gpio.output(self.in2, gpio.LOW)

        # Initialize PWM for speed control
        self.pwm = gpio.PWM(self.enable, 1000)  # 1 kHz PWM frequency
        self.pwm.start(0)  # Start with 0% duty cycle (motor off)

    def __del__(self) -> None:
        """
        Cleans up GPIO resources when the object is deleted.
        """
        self.pwm.stop()  # Stop PWM
        gpio.cleanup()  # Reset GPIO settings

    def run(self, speed: float) -> None:
        """
        Runs the motor at the specified speed.

        Args:
            speed (float): Speed percentage (-100.0 to 100.0).
                           - Positive values move the motor forward.
                           - Negative values move the motor backward.
                           - Zero stops the motor.
        """
        # Constrain speed within valid range
        speed = max(min(speed, 100.0), -100.0)

        # Adjust PWM duty cycle to control motor speed
        self.pwm.ChangeDutyCycle(abs(speed))

        if speed == 0:
            # Stop motor
            gpio.output(self.in1, gpio.LOW)
            gpio.output(self.in2, gpio.LOW)
        elif speed > 0:
            # Move forward
            gpio.output(self.in1, gpio.HIGH)
            gpio.output(self.in2, gpio.LOW)
        else:
            # Move backward
            gpio.output(self.in1, gpio.LOW)
            gpio.output(self.in2, gpio.HIGH)