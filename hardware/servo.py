from typing import Tuple
from adafruit_servokit import ServoKit


class Servo:
    """
    Controls an individual servo motor using the Adafruit ServoKit library.

    This class provides methods for setting and adjusting the servo angle
    while enforcing movement constraints.
    """

    def __init__(self, kit: ServoKit, channel: int, actuation_range: int, limits: Tuple[float, float]) -> None:
        """
        Initializes the servo motor.

        Args:
            kit (ServoKit): The Adafruit ServoKit instance for controlling the servo.
            channel (int): The servo channel (0-15).
            actuation_range (int): The full range of motion for the servo (in degrees).
            limits (Tuple[float, float]): Minimum and maximum allowed angles (in degrees).
        """
        self.servo = kit.servo[channel]  # Assign the correct servo channel
        self.range: int = actuation_range  # Store actuation range
        self.limits: Tuple[float, float] = limits  # Store movement limits
        self.servo.actuation_range = actuation_range  # Apply actuation range to the servo
        self.curr_angle: float = 0.0  # Initialize the current angle

    def __del__(self) -> None:
        """
        Deactivates the servo by setting its angle to `None` (turning it off).
        """
        self.servo.angle = None  # Disables the servo

    def set_angle(self, angle: float) -> None:
        """
        Sets the servo to a specific angle while enforcing movement limits.

        Args:
            angle (float): Desired servo angle in degrees.
        """
        # Adjust angle based on actuation range
        angle = angle + self.range / 2

        # Ensure the angle remains within defined limits
        if angle < self.limits[0]:
            angle = self.limits[0]
        if angle > self.limits[1]:
            angle = self.limits[1]

        # Apply the angle to the servo
        self.servo.angle = angle
        self.curr_angle = angle  # Update current angle state

    def add_angle(self, angle: float) -> None:
        """
        Increments or decrements the servo angle by a given amount.

        Args:
            angle (float): The amount to adjust the angle by (positive or negative).
        """
        new_angle = self.curr_angle + angle
        self.set_angle(new_angle)  # Use `set_angle` to apply new value while enforcing limits