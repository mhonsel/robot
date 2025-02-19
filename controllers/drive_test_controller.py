import math
import time
from controllers.pid import PID

class DriveTestController:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.name = 'Drive Test'

        # create the PID and initialize it
        self.drive_pid = PID(kP=0.035, kI=0.0004, kD=0.00001)
        self.drive_pid.initialize()

        self.start_time = time.time()

    def __del__(self):
        self.supervisor.v = 0.0
        self.supervisor.omega = 0.0

    def update(self):
#        self.supervisor.v = 0.2
        self.supervisor.omega = math.pi
