import cv2

from aiymakerkit import vision
from aiymakerkit import utils

# local imports
import data.models as models
from controllers.pid import PID

class PanTiltController:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.name = 'Pan Tilt'

        
        if self.supervisor.has_vision:
            # calculate the center of the frame as this is where we will
            # try to keep the object
            (H, W) = self.supervisor.image.shape[:2]
            self.center_x = W // 2
            self.center_y = H // 2

            # initialize detector
            if self.supervisor.target_object == 'face':
                self.detector = vision.Detector(models.FACE_DETECTION_MODEL)
                self.labels = None
                self.threshold = 0.1
            else:
                self.detector = vision.Detector(models.OBJECT_DETECTION_MODEL)
                self.labels = utils.read_labels_from_metadata(models.OBJECT_DETECTION_MODEL)
                self.threshold = 0.4

            # create the pan/tilt PIDs and initialize them
            self.pan_pid = PID(kP=0.035, kI=0.0004, kD=0.0001)
            self.pan_pid.initialize(offset=self.supervisor.pan)
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

                # update the pid controllers
                pan_error = self.center_x - obj_x 
                self.supervisor.pan = self.pan_pid.update(pan_error)
                tilt_error = self.center_y - obj_y 
#                print('Tilt Error: {}'.format(tilt_error))
                self.supervisor.tilt = self.tilt_pid.update(tilt_error)
#                print('Tilt: {}'.format(self.supervisor.tilt))

            # otherwise no objects were found
            else:
                self.supervisor.pan = self.pan_pid.update(0)
                self.supervisor.tilt = self.tilt_pid.update(0)
