class Servo:
    # initialize servo
    def __init__(self, kit, channel, actuation_range, limits):
        self.servo = kit.servo[channel]
        self.range = actuation_range
        self.limits = limits
        self.servo.actuation_range = actuation_range
        self.curr_angle = 0.0

    # deactivate servos
    def __del__(self):
        self.servo.angle = None

    def set_angle(self, angle):
        angle = angle + self.range/2
        if angle < self.limits[0]:
            angle = self.limits[0]
        if angle > self.limits[1]:
            angle = self.limits[1]
        
        self.servo.angle = angle
        self.curr_angle = angle

    def add_angle(self, angle):
        new_angle = self.curr_angle + angle
        self.set_angle(new_angle)
