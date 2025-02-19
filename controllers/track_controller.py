import cv2
from aiymakerkit import vision, utils

# Local imports
import data.models as models
from controllers.pid import PID


class TrackController:
    """
    A controller for tracking a specified object using computer vision.

    The robot uses a vision-based detector and PID controllers to adjust its
    pan, tilt, and movement to keep the target object centered in the frame.
    """

    def __init__(self, supervisor) -> None:
        """
        Initializes the TrackController.

        Args:
            supervisor: The Supervisor instance managing the robot's state.
        """
        self.supervisor = supervisor
        self.name: str = "Track"

        if self.supervisor.has_vision:
            # Get image dimensions
            self.image_height: int = self.supervisor.image.shape[0]
            self.image_width: int = self.supervisor.image.shape[1]
            self.image_size: int = self.image_height * self.image_width  # Total image area
            self.center_x: int = self.image_width // 2  # X-coordinate of image center
            self.center_y: int = self.image_height // 2  # Y-coordinate of image center

            # Initialize object detection model
            self.model: str = models.OBJECT_DETECTION_MODEL
            self.labels = utils.read_labels_from_metadata(models.OBJECT_DETECTION_MODEL)

            # Configure detection parameters based on target object type
            if self.supervisor.target_object == "face":
                self.model = models.FACE_DETECTION_MODEL
                self.threshold: float = 0.1  # Lower threshold for face detection
                self.goal_size: float = 0.15  # Target object size ratio in frame
                self.supervisor.tilt = 45  # Adjust tilt angle for face tracking
            elif self.supervisor.target_object == "person":
                self.goal_size: float = 0.75
                self.supervisor.tilt = 30  # Adjust tilt for body tracking
                self.threshold: float = 0.6  # Higher threshold for person detection
            else:
                self.goal_size: float = 0.3
                self.threshold: float = 0.4

            self.detector = vision.Detector(self.model)  # Initialize detector

            # Initialize PID controllers for turning and tilting
            self.turn_pid = PID(kP=0.003, kI=0.00000, kD=0.00000)
            self.turn_pid.initialize(offset=self.supervisor.omega)

            self.tilt_pid = PID(kP=0.06, kI=0.0006, kD=0.0002)
            self.tilt_pid.initialize(offset=self.supervisor.tilt)

    def update(self) -> None:
        """
        Updates the robot's movement to track the target object.

        The robot will adjust its pan, tilt, and velocity to maintain the
        object at the center of the frame.
        """
        if self.supervisor.has_vision:
            # Run object detection
            objects = self.detector.get_objects(self.supervisor.image, threshold=self.threshold)

            # Filter objects based on the target object type
            if self.supervisor.target_object != "face":
                objects = [o for o in objects if self.labels.get(o.id) == self.supervisor.target_object]

            if objects:
                # Draw bounding boxes and labels on the detected objects
                vision.draw_objects(self.supervisor.image, objects, self.labels)

                # Extract bounding box coordinates of the first detected object
                (x_min, y_min, x_max, y_max) = objects[0].bbox
                obj_x: int = int((x_min + x_max) / 2.0)  # Center X-coordinate of object
                obj_y: int = int((y_min + y_max) / 2.0)  # Center Y-coordinate of object
                obj_size: float = (x_max - x_min) * (y_max - y_min)  # Object area

                # Compute tracking errors for pan and tilt
                turn_error: int = self.center_x - obj_x  # Horizontal offset from center
                self.supervisor.omega = self.turn_pid.update(turn_error)  # Adjust turning

                tilt_error: int = self.center_y - obj_y  # Vertical offset from center
                self.supervisor.tilt = self.tilt_pid.update(tilt_error)  # Adjust tilting

                # Compute drive error (distance adjustment based on object size)
                drive_error: float = 1 - min(obj_size / (self.image_size * self.goal_size), 1)

                # Compute velocity adjustment (speed decreases with larger omega)
                drive_max: float = 0.4  # Maximum velocity (m/s)
                self.supervisor.v = (drive_error * drive_max) / (abs(self.supervisor.omega) + 1) ** 0.5

            else:
                # If no objects are found, reset movements
                self.supervisor.omega = self.turn_pid.update(0)
                self.supervisor.tilt = self.tilt_pid.update(0)
                self.supervisor.v = 0  # Stop moving forward