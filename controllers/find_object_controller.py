import cv2
import math
import threading
import time

from aiymakerkit import vision
from aiymakerkit import utils

# local imports
import data.models as models

class FindObjectController:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.name = 'Find Object'

        if self.supervisor.has_vision:
            # initialize detector
            if self.supervisor.target_object == 'face':
                self.detector = vision.Detector(models.FACE_DETECTION_MODEL)
                self.labels = None
                self.threshold = 0.1
            else:
                self.detector = vision.Detector(models.OBJECT_DETECTION_MODEL)
                self.labels = utils.read_labels_from_metadata(models.OBJECT_DETECTION_MODEL)
                self.threshold = 0.4

            # set up scanning thread
            self.detection = threading.Event()
            self.scanning_thread = threading.Thread(target=self.scan_drive, daemon=True)
            self.scanning_thread.start()

    def __del__(self):
        with self.supervisor._lock:
            self.supervisor.omega = 0
            self.supervisor.v = 0

    def update(self):
        # only run when there's an image from the camera
        if self.supervisor.has_vision:
            # run detector
            objects = self.detector.get_objects(self.supervisor.image, threshold=self.threshold)

            # only objects matching the target object
            if not self.supervisor.target_object == 'face':
                objects = [o for o in objects if self.labels.get(o.id) == self.supervisor.target_object]

            if objects:
                # set detection flag
                self.detection.set()

                # draw bounding boxes and labels
                vision.draw_objects(self.supervisor.image, objects, self.labels)

    def scan_pan_tilt(self, scan_speed = 0.5):
        tilt_angles = list(range(0, 60, 30))
        pan_angles = list(range(-90, 91, 30))

        # Scan continuously
        while True:
            # Iterate over tilt angles
            for tilt in tilt_angles:
                if self.detection.is_set():
                    return
                with self.supervisor._lock:
                    self.supervisor.tilt = tilt

                # Iterate over pan angles
                for pan in pan_angles:
                    time.sleep(scan_speed)

                    if self.detection.is_set():

                        return
                    with self.supervisor._lock:
                        self.supervisor.pan = pan

                # Go in reverse
                pan_angles.reverse()
            tilt_angles.reverse()

    def scan_drive(self, scan_speed = 1.5):
#        tilt_angles = list(range(0, 60, 30))
        tilt_angles = [0]
        turn_time = (2 * math.pi) / scan_speed # time for 360 degree turn

        # Start turning in place
        with self.supervisor._lock:
            self.supervisor.omega = scan_speed

        # Scan continuously
        while True:
            # Iterate over tilt angles
            for tilt in tilt_angles:
                if self.detection.is_set():
                    return
                with self.supervisor._lock:
                    self.supervisor.tilt = tilt

                # Make one full 360 degree turn
                start_time = time.time()
                while ((time.time() - start_time) < turn_time):
                    if self.detection.is_set():
                        with self.supervisor._lock:
                            self.supervisor.omega = 0
                        return
            tilt_angles.reverse()

