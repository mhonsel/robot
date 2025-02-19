import utils.drive

class FourWheelDiffDrive:
    def __init__(self, robot):
        # robot
        self.robot = robot
        self.R = self.robot.wheel_radius
        self.T = self.robot.wheel_track

        # defaults
        self.lf_motor_r = 0.0
        self.rf_motor_r = 0.0
        self.lb_motor_r = 0.0
        self.rb_motor_r = 0.0

    def update(self):
        v = self.robot.v
        omega = self.robot.omega

        v_l, v_r = utils.drive.uni_to_diff(v, omega, self.R, self.T)

#        print(v)

        # Temporary to calibrate values to m/s 
#        r_l = v_l * 4.43
#        r_r = v_r * 4.43
        r_l = v_l * 4.43 * 2
        r_r = v_r * 4.43 * 2

#        print("Left rate: %f, right rate: %f" % (r_l, r_r))

        self.robot.lf_motor.run(r_l)
        self.robot.rf_motor.run(r_r)
        self.robot.lb_motor.run(r_l)
        self.robot.rb_motor.run(r_r)
