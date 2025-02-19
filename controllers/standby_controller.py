class StandbyController:
    """
    A controller that keeps the robot in a standby state.

    This controller is used when the robot is idle and not executing any movement
    or object tracking operations.
    """

    def __init__(self, supervisor) -> None:
        """
        Initializes the StandbyController.

        Args:
            supervisor: The Supervisor instance managing the robot's state.
        """
        self.supervisor = supervisor  # Store reference to the robot's supervisor
        self.name: str = "Standby"  # Set controller name

    def update(self) -> None:
        """
        Keeps the robot in standby mode.

        This method is a placeholder for future standby behavior, such as
        running low-power routines or waiting for user input.
        """
        pass  # No action is performed in standby mode