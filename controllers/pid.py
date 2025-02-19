import time


class PID:
    """
    Implements a simple PID (Proportional-Integral-Derivative) controller.

    The PID controller adjusts a control variable based on proportional, integral,
    and derivative terms calculated from error values over time.
    """

    def __init__(self, kP: float = 1.0, kI: float = 0.0, kD: float = 0.0) -> None:
        """
        Initializes the PID controller with given gain values.

        Args:
            kP (float, optional): Proportional gain. Defaults to 1.0.
            kI (float, optional): Integral gain. Defaults to 0.0.
            kD (float, optional): Derivative gain. Defaults to 0.0.
        """
        self.kP: float = kP  # Proportional gain
        self.kI: float = kI  # Integral gain
        self.kD: float = kD  # Derivative gain

    def initialize(self, offset: float = 0.0) -> None:
        """
        Initializes PID variables, including time tracking and error terms.

        Args:
            offset (float, optional): Initial offset value for integral term. Defaults to 0.0.
        """
        # Initialize time tracking
        self.currTime: float = time.time()
        self.prevTime: float = self.currTime

        # Initialize previous error
        self.prevError: float = 0.0

        # Initialize PID terms
        self.cP: float = 0.0  # Proportional term
        self.cI: float = (offset / self.kI) if self.kI > 0 else 0.0  # Integral term
        self.cD: float = 0.0  # Derivative term

    def update(self, error: float, sleep: float = 0.0) -> float:
        """
        Updates the PID controller with a new error value and computes the control output.

        Args:
            error (float): The current error value.
            sleep (float, optional): Optional delay before computing the update (in seconds). Defaults to 0.0.

        Returns:
            float: The computed control output based on PID calculations.
        """
        # Pause for the specified duration (if any)
        time.sleep(sleep)

        # Capture the current time and compute time difference
        self.currTime = time.time()
        deltaTime: float = self.currTime - self.prevTime

        # Compute change in error
        deltaError: float = error - self.prevError

        # Compute PID terms
        self.cP = error  # Proportional term
        self.cI += error * deltaTime  # Integral term

        # Compute derivative term (avoid division by zero)
        self.cD = (deltaError / deltaTime) if deltaTime > 0 else 0.0

        # Save previous time and error for the next update
        self.prevTime = self.currTime
        self.prevError = error

        # Compute and return the control output
        return sum([
            self.kP * self.cP,
            self.kI * self.cI,
            self.kD * self.cD
        ])