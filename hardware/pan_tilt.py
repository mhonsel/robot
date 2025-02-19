from hardware.servo import Servo

class PanTilt:
    def __init__(self, robot):
        # robot
        self.robot = robot

        # set up pan/tilt servos
        self.pan_servo = Servo(self.robot.servo_kit, 0, 180, (0, 180))
        self.pan_servo.set_angle(0)
        self.tilt_servo = Servo(self.robot.servo_kit, 1, 180, (30, 150))
        self.tilt_servo.set_angle(0)

    def __del__(self):
        del self.pan_servo
        del self.tilt_servo

    def pan(self, angle):
        self.pan_servo.set_angle(angle)

    def tilt(self, angle):
        # reverse direction of tilt servo
        self.tilt_servo.set_angle(-angle)

    def update(self):
        self.pan(self.robot.pan)
        self.tilt(self.robot.tilt)
