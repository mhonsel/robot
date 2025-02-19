from hardware.servo import Servo


class PanTilt:
    """
    Controls a pan-tilt mechanism using two servos.

    The pan servo rotates horizontally, while the tilt servo adjusts the vertical angle.
    """

    def __init__(self, robot) -> None:
        """
        Initializes the pan-tilt servos.

        Args:
            robot: The robot instance containing the servo control interface.
        """
        # Store reference to the robot
        self.robot = robot

        # Initialize pan servo (channel 0, 0° to 180° range)
        self.pan_servo = Servo(self.robot.servo_kit, channel=0, pwm_range=180, angle_limits=(0, 180))
        self.pan_servo.set_angle(0)  # Start at neutral position

        # Initialize tilt servo (channel 1, limited to 30°-150° to avoid overextension)
        self.tilt_servo = Servo(self.robot.servo_kit, channel=1, pwm_range=180, angle_limits=(30, 150))
        self.tilt_servo.set_angle(0)  # Start at neutral position

    def __del__(self) -> None:
        """
        Cleans up resources when the object is deleted.
        """
        del self.pan_servo
        del self.tilt_servo

    def pan(self, angle: float) -> None:
        """
        Sets the pan (horizontal rotation) angle.

        Args:
            angle (float): Desired pan angle in degrees.
        """
        self.pan_servo.set_angle(angle)

    def tilt(self, angle: float) -> None:
        """
        Sets the tilt (vertical rotation) angle.

        Args:
            angle (float): Desired tilt angle in degrees. This is reversed due to servo orientation.
        """
        self.tilt_servo.set_angle(-angle)  # Invert angle to match physical servo direction

    def update(self) -> None:
        """
        Updates the pan-tilt servos based on the robot's current pan and tilt angles.
        """
        self.pan(self.robot.pan)
        self.tilt(self.robot.tilt)