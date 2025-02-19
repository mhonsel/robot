import cv2
from adafruit_servokit import ServoKit

# Local imports
from supervisor import Supervisor
from hardware.pan_tilt import PanTilt
from hardware.motor import Motor
from hardware.drive import FourWheelDiffDrive
from hardware.display import Display

# Camera and frame capture settings
CAMERA_ID: int = 0
CAPTURE_WIDTH: int = 640
CAPTURE_HEIGHT: int = 480

# Motor pin configurations (enable, in1, in2)
LB_MOTOR_PINS: tuple[int, int, int] = (17, 27, 22)
RB_MOTOR_PINS: tuple[int, int, int] = (11, 9, 10)
LF_MOTOR_PINS: tuple[int, int, int] = (23, 24, 25)
RF_MOTOR_PINS: tuple[int, int, int] = (12, 7, 8)

# Robot physical properties
WHEEL_RADIUS: float = 0.033  # Wheel radius in meters
WHEEL_TRACK: float = 0.136  # Distance between wheels in meters


class Robot:
    """A self-driving robot that uses computer vision to track and follow people."""

    def __init__(self) -> None:
        """Initializes the robot's hardware, camera, and control systems."""
        # Store robot dimensions
        self.wheel_radius: float = WHEEL_RADIUS
        self.wheel_track: float = WHEEL_TRACK

        # Initialize motors
        self.lf_motor = Motor(LF_MOTOR_PINS)
        self.rf_motor = Motor(RF_MOTOR_PINS)
        self.lb_motor = Motor(LB_MOTOR_PINS)
        self.rb_motor = Motor(RB_MOTOR_PINS)

        # Differential drive system
        self.drive = FourWheelDiffDrive(self)

        # Servo control for pan-tilt system
        self.servo_kit = ServoKit(channels=16, frequency=50)
        self.pan_tilt = PanTilt(self)

        # Display setup (for status/output)
        self.display = Display()

        # Initialize camera for image capture
        self.camera_id: int = CAMERA_ID
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

        # Supervisor (handles AI-based decision-making)
        self.supervisor = Supervisor(self)

        # Initial movement states
        self.pan: float = 0.0  # Horizontal pan angle
        self.tilt: float = 0.0  # Vertical tilt angle
        self.v: float = 0.0  # Linear velocity
        self.omega: float = 0.0  # Angular velocity

    def __del__(self) -> None:
        """Cleans up resources when the robot is destroyed."""
        # Release motors
        del self.lf_motor
        del self.rf_motor
        del self.lb_motor
        del self.rb_motor

        # Release pan-tilt system
        del self.pan_tilt

        # Release camera resources
        self.cap.release()

    def update(self) -> None:
        """Updates the robot's subsystems, including pan-tilt and driving."""
        self.pan_tilt.update()  # Adjust pan-tilt angles based on tracking
        self.drive.update()  # Update motor controls