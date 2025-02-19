import math
import time
from controllers.pid import PID


class DriveTestController:
    """
    A test controller for driving the robot using a PID controller.

    This controller is primarily used for testing movement and ensuring
    the robot's velocity and angular velocity behave as expected.
    """

    def __init__(self, supervisor) -> None:
        """
        Initializes the DriveTestController.

        Args:
            supervisor: The Supervisor instance managing the robot's state.
        """
        self.supervisor = supervisor  # Reference to the robot supervisor
        self.name: str = "Drive Test"  # Controller name

        # Initialize the PID controller for driving
        self.drive_pid = PID(kP=0.035, kI=0.0004, kD=0.00001)
        self.drive_pid.initialize()

        # Store the start time for potential time-based movement tests
        self.start_time: float = time.time()

    def __del__(self) -> None:
        """
        Ensures the robot stops when the controller is deleted.
        """
        self.supervisor.v = 0.0  # Stop linear velocity
        self.supervisor.omega = 0.0  # Stop angular velocity

    def update(self) -> None:
        """
        Updates the robot's movement commands.
        """
        # Uncomment the line below to set a constant forward velocity for testing.
        # self.supervisor.v = 0.2  # Set a small forward speed (m/s)

        # Set angular velocity to π rad/s (full rotation per second)
        self.supervisor.omega = math.pi