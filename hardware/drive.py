import utils.drive


class FourWheelDiffDrive:
    """
    Implements a four-wheel differential drive system for the robot.
    Converts desired translational and rotational velocities into wheel speeds.
    """

    def __init__(self, robot) -> None:
        """
        Initializes the differential drive system.

        Args:
            robot: The robot instance containing motor control and kinematic parameters.
        """
        # Reference to the robot instance
        self.robot = robot

        # Wheel and track parameters
        self.R: float = self.robot.wheel_radius  # Wheel radius (m)
        self.T: float = self.robot.wheel_track  # Distance between wheels (m)

        # Motor speed defaults (rad/s)
        self.lf_motor_r: float = 0.0  # Left front wheel speed
        self.rf_motor_r: float = 0.0  # Right front wheel speed
        self.lb_motor_r: float = 0.0  # Left back wheel speed
        self.rb_motor_r: float = 0.0  # Right back wheel speed

    def update(self) -> None:
        """
        Updates the motor speeds based on the robot's desired velocity and angular velocity.
        """
        # Retrieve desired translational and angular velocity from the robot
        v: float = self.robot.v  # Translational velocity (m/s)
        omega: float = self.robot.omega  # Angular velocity (rad/s)

        # Convert unicycle model velocities to differential drive velocities
        v_l, v_r = utils.drive.uni_to_diff(v, omega, self.R, self.T)

        # Scaling factor to convert from computed velocity to motor input speed
        SCALING_FACTOR: float = 4.43 * 2  # Empirical factor for motor speed calibration

        # Compute motor speeds
        r_l: float = v_l * SCALING_FACTOR  # Left wheel speed (scaled)
        r_r: float = v_r * SCALING_FACTOR  # Right wheel speed (scaled)

        # Apply computed speeds to all four motors
        self.robot.lf_motor.run(r_l)  # Left front motor
        self.robot.rf_motor.run(r_r)  # Right front motor
        self.robot.lb_motor.run(r_l)  # Left back motor
        self.robot.rb_motor.run(r_r)  # Right back motor