import cv2
from adafruit_servokit import ServoKit

# local imports
from supervisor import Supervisor
from hardware.pan_tilt import PanTilt
from hardware.motor import Motor
from hardware.drive import FourWheelDiffDrive
from hardware.display import Display

CAMERA_ID = 0
CAPTURE_WIDTH = 640
CAPTURE_HEIGHT = 480

LB_MOTOR_PINS = (17, 27, 22) # (en, in1, in2)
RB_MOTOR_PINS = (11, 9, 10)
LF_MOTOR_PINS = (23, 24, 25)
RF_MOTOR_PINS = (12, 7, 8)

WHEEL_RADIUS = 0.033
WHEEL_TRACK = 0.136

class Robot:
    def __init__(self):
        # hardware setup
        # dimensions
        self.wheel_radius = WHEEL_RADIUS
        self.wheel_track = WHEEL_TRACK

        # motors and drive setup
        self.lf_motor = Motor(LF_MOTOR_PINS)
        self.rf_motor = Motor(RF_MOTOR_PINS)
        self.lb_motor = Motor(LB_MOTOR_PINS)
        self.rb_motor = Motor(RB_MOTOR_PINS)
        self.drive = FourWheelDiffDrive(self)

        # servos and pan tilt setups
        self.servo_kit = ServoKit(channels=16, frequency=50)
        self.pan_tilt = PanTilt(self)

        # display
        self.display = Display()

        # set up image capture
        self.camera_id = CAMERA_ID
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

        # supervisor
        self.supervisor = Supervisor(self)

        # initial state
        self.pan = 0.0
        self.tilt = 0.0
        self.v = 0.0
        self.omega = 0.0

    def __del__(self):
        # cleanup
        # motors
        del self.lf_motor
        del self.rf_motor
        del self.lb_motor
        del self.rb_motor

        # servos
        del self.pan_tilt

        # camera
        self.cap.release()

    def update(self):
        self.pan_tilt.update()
        self.drive.update()

