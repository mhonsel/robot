import cv2
import math
import threading
import time

from aiymakerkit import vision
from aiymakerkit import utils

# Local imports
import data.models as models


class FindObjectController:
    """
    A controller for detecting and tracking objects using computer vision.

    This controller searches for a specified object (e.g., face or general object)
    using a detector and adjusts the robot's motion accordingly.
    """

    def __init__(self, supervisor) -> None:
        """
        Initializes the FindObjectController.

        Args:
            supervisor: The Supervisor instance managing the robot's state.
        """
        self.supervisor = supervisor
        self.name: str = "Find Object"

        if self.supervisor.has_vision:
            # Initialize the detector based on the target object
            if self.supervisor.target_object == "face":
                self.detector = vision.Detector(models.FACE_DETECTION_MODEL)
                self.labels = None
                self.threshold: float = 0.1  # Lower threshold for face detection
            else:
                self.detector = vision.Detector(models.OBJECT_DETECTION_MODEL)
                self.labels = utils.read_labels_from_metadata(models.OBJECT_DETECTION_MODEL)
                self.threshold: float = 0.4  # Higher threshold for general object detection

            # Set up scanning thread for continuous object searching
            self.detection = threading.Event()
            self.scanning_thread = threading.Thread(target=self.scan_drive, daemon=True)
            self.scanning_thread.start()

    def __del__(self) -> None:
        """
        Ensures the robot stops moving when the controller is deleted.
        """
        with self.supervisor._lock:
            self.supervisor.omega = 0  # Stop angular velocity
            self.supervisor.v = 0  # Stop linear velocity

    def update(self) -> None:
        """
        Runs object detection on the latest camera frame and updates the robot's behavior.
        """
        if self.supervisor.has_vision:
            # Run the object detector on the current camera frame
            objects = self.detector.get_objects(self.supervisor.image, threshold=self.threshold)

            # Filter detected objects to match the target object (if not detecting faces)
            if self.supervisor.target_object != "face":
                objects = [o for o in objects if self.labels.get(o.id) == self.supervisor.target_object]

            if objects:
                # Object detected, set detection flag
                self.detection.set()

                # Draw bounding boxes and labels on the image
                vision.draw_objects(self.supervisor.image, objects, self.labels)

    def scan_pan_tilt(self, scan_speed: float = 0.5) -> None:
        """
        Scans the environment by moving the pan-tilt mechanism in a sweeping motion.

        Args:
            scan_speed (float): Delay time (in seconds) between pan/tilt adjustments.
        """
        tilt_angles = list(range(0, 60, 30))  # Tilt angles from 0° to 60°
        pan_angles = list(range(-90, 91, 30))  # Pan angles from -90° to 90°

        # Perform a continuous scanning motion
        while True:
            for tilt in tilt_angles:
                if self.detection.is_set():
                    return
                with self.supervisor._lock:
                    self.supervisor.tilt = tilt

                for pan in pan_angles:
                    time.sleep(scan_speed)
                    if self.detection.is_set():
                        return
                    with self.supervisor._lock:
                        self.supervisor.pan = pan

                # Reverse pan angle order for next cycle
                pan_angles.reverse()
            tilt_angles.reverse()

    def scan_drive(self, scan_speed: float = 1.5) -> None:
        """
        Rotates the robot in place while scanning for an object.

        Args:
            scan_speed (float): Angular speed (rad/s) of the robot while scanning.
        """
        tilt_angles = [0]  # Keep tilt at 0° while scanning
        turn_time: float = (2 * math.pi) / scan_speed  # Time for a full 360° turn

        # Start turning in place
        with self.supervisor._lock:
            self.supervisor.omega = scan_speed

        # Perform a continuous scanning motion
        while True:
            for tilt in tilt_angles:
                if self.detection.is_set():
                    return
                with self.supervisor._lock:
                    self.supervisor.tilt = tilt

                # Rotate for a full 360° turn
                start_time = time.time()
                while (time.time() - start_time) < turn_time:
                    if self.detection.is_set():
                        with self.supervisor._lock:
                            self.supervisor.omega = 0  # Stop rotation
                        return

            # Reverse tilt angles for next cycle
            tilt_angles.reverse()