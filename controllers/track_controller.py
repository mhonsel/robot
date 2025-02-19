import cv2

from aiymakerkit import vision
from aiymakerkit import utils

# local imports
import data.models as models
from controllers.pid import PID

class TrackController:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.name = 'Track'

        
        if self.supervisor.has_vision:
            # calculate the center of the frame as this is where we will
            # try to keep the object
            (self.image_height, self.image_width) = self.supervisor.image.shape[:2]
            self.image_size = self.image_height * self.image_width
            self.center_x = self.image_width // 2
            self.center_y = self.image_height // 2

            # initialize detector
            self.model = models.OBJECT_DETECTION_MODEL
            self.labels = utils.read_labels_from_metadata(models.OBJECT_DETECTION_MODEL)

            if self.supervisor.target_object == 'face':
                model = models.FACE_DETECTION_MODEL
                self.threshold = 0.1
                self.goal_size = 0.15
                self.supervisor.tilt = 45
            elif self.supervisor.target_object == 'person':
                self.goal_size = 0.75
                self.supervisor.tilt = 30
                self.threshold = 0.6
            else:
                self.goal_size = 0.3
                self.threshold = 0.4

            self.detector = vision.Detector(self.model)

            # create the turn/tilt PIDs and initialize them
            self.turn_pid = PID(kP=0.003, kI=0.00000, kD=0.00000)
            self.turn_pid.initialize(offset=self.supervisor.omega)
            self.tilt_pid = PID(kP=0.06, kI=0.0006, kD=0.0002)
            self.tilt_pid.initialize(offset=self.supervisor.tilt)

    def update(self):
        # only run when there's an image from the camera
        if self.supervisor.has_vision:
            # run detector
            objects = self.detector.get_objects(self.supervisor.image, threshold=self.threshold)

            # only objects matching the target object
            if not self.supervisor.target_object == 'face':
                objects = [o for o in objects if self.labels.get(o.id) == self.supervisor.target_object]

            if objects:
                # draw bounding boxes and labels
                vision.draw_objects(self.supervisor.image, objects, self.labels)

                # extract the bounding box coordinates of the object and
                # use the coordinates to determine the center
                (x_min, y_min, x_max, y_max) = objects[0].bbox 
                obj_x = int((x_min + x_max) / 2.0)
                obj_y = int((y_min + y_max) / 2.0)
                obj_size = (x_max - x_min) * (y_max - y_min)

                # update the pid controllers
                turn_error = self.center_x - obj_x 
#                print('Turn Error: {}'.format(turn_error))
#                print('Turn: {}'.format(self.turn_pid.update(turn_error)))
                self.supervisor.omega = self.turn_pid.update(turn_error)

                tilt_error = self.center_y - obj_y 
                self.supervisor.tilt = self.tilt_pid.update(tilt_error)

                drive_error = 1 - min(obj_size / (self.image_size * self.goal_size), 1) 
#                print('Drive Error: {}'.format(drive_error))
                drive_max = 0.4 # m/s
                v = (drive_error * drive_max) / (abs(self.supervisor.omega) + 1)**0.5
                self.supervisor.v = v
 

            # otherwise no objects were found
            else:
                self.supervisor.omega = self.turn_pid.update(0)
                self.supervisor.tilt = self.tilt_pid.update(0)
                self.supervisor.v = 0
