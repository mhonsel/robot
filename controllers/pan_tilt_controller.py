import cv2
from aiymakerkit import vision, utils

# Local imports
import data.models as models
from controllers.pid import PID


class PanTiltController:
    """
    A controller for adjusting the robot's pan-tilt mechanism to track objects.

    Uses a vision-based detector and PID controllers to align the robot's camera
    with a target object in the frame.
    """

    def __init__(self, supervisor) -> None:
        """
        Initializes the PanTiltController.

        Args:
            supervisor: The Supervisor instance managing the robot's state.
        """
        self.supervisor = supervisor
        self.name: str = "Pan Tilt"

        if self.supervisor.has_vision:
            # Calculate the center of the frame (target tracking position)
            (H, W) = self.supervisor.image.shape[:2]
            self.center_x: int = W // 2  # Center X-coordinate of the frame
            self.center_y: int = H // 2  # Center Y-coordinate of the frame

            # Initialize object detection model based on target type
            if self.supervisor.target_object == "face":
                self.detector = vision.Detector(models.FACE_DETECTION_MODEL)
                self.labels = None
                self.threshold: float = 0.1  # Lower threshold for face detection
            else:
                self.detector = vision.Detector(models.OBJECT_DETECTION_MODEL)
                self.labels = utils.read_labels_from_metadata(models.OBJECT_DETECTION_MODEL)
                self.threshold: float = 0.4  # Higher threshold for object detection

            # Initialize PID controllers for pan and tilt adjustments
            self.pan_pid = PID(kP=0.035, kI=0.0004, kD=0.0001)
            self.pan_pid.initialize(offset=self.supervisor.pan)

            self.tilt_pid = PID(kP=0.06, kI=0.0006, kD=0.0002)
            self.tilt_pid.initialize(offset=self.supervisor.tilt)

    def update(self) -> None:
        """
        Updates the pan-tilt servos based on object detection.

        If an object is detected, the servos adjust to align the camera
        with the target's position in the frame.
        """
        if self.supervisor.has_vision:
            # Run object detection on the current camera frame
            objects = self.detector.get_objects(self.supervisor.image, threshold=self.threshold)

            # Filter detected objects to match the target object (if not detecting faces)
            if self.supervisor.target_object != "face":
                objects = [o for o in objects if self.labels.get(o.id) == self.supervisor.target_object]

            if objects:
                # Draw bounding boxes and labels on the image
                vision.draw_objects(self.supervisor.image, objects, self.labels)

                # Extract bounding box coordinates of the first detected object
                (x_min, y_min, x_max, y_max) = objects[0].bbox
                obj_x: int = int((x_min + x_max) / 2.0)  # Compute object's center X-coordinate
                obj_y: int = int((y_min + y_max) / 2.0)  # Compute object's center Y-coordinate

                # Compute tracking errors and update PID controllers
                pan_error: int = self.center_x - obj_x  # Horizontal offset from center
                self.supervisor.pan = self.pan_pid.update(pan_error)  # Adjust pan angle

                tilt_error: int = self.center_y - obj_y  # Vertical offset from center
                self.supervisor.tilt = self.tilt_pid.update(tilt_error)  # Adjust tilt angle

            else:
                # If no objects were detected, reset pan and tilt adjustments
                self.supervisor.pan = self.pan_pid.update(0)
                self.supervisor.tilt = self.tilt_pid.update(0)