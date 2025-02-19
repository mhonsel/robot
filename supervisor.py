import cv2
import sys
import threading
import time

from aiymakerkit import audio

# Local imports
import data.models as models
from controllers.standby_controller import StandbyController
from controllers.pan_tilt_controller import PanTiltController
from controllers.track_controller import TrackController
from controllers.find_object_controller import FindObjectController
from controllers.drive_test_controller import DriveTestController

# Voice command configuration
VOICE_CONFIDENCE_SCORE: float = 0.5
SUPPORTED_COMMANDS: tuple[str, ...] = ('wait', 'drive', 'track', 'find', 'goodbye')


class Supervisor:
    """Manages the high-level behavior of the robot, handling vision, control, and commands."""

    def __init__(self, robot) -> None:
        """
        Initializes the Supervisor, which oversees robot control and state management.

        Args:
            robot: The robot instance to be supervised.
        """
        self.robot = robot

        # Threading locks and shutdown flag
        self._lock = threading.RLock()
        self.shutdown = threading.Event()

        # Initial movement states
        self.pan: float = 0.0
        self.tilt: float = 0.0
        self.v: float = 0.0
        self.omega: float = 0.0
        self._command: str = 'wait'
        self._target_object: str = ''

        # Controller for handling robot behavior
        self._current_controller = StandbyController(self)

        # Initialize vision system
        self._update_vision()

        # Status messages for display/debugging
        self.status_msg: dict[str, str] = {
            'command': f'Command: {self.command}',
            'target_object': f'Target: {self.target_object}',
            'controller': f'Controller: {self.current_controller.name}',
        }

    @property
    def command(self) -> str:
        """Gets the current command."""
        return self._command

    @command.setter
    def command(self, new_command: str) -> None:
        """Sets a new command and updates the status message."""
        with self._lock:
            self._command = new_command
        self.status_msg['command'] = f'Command: {self.command}'

    @property
    def target_object(self) -> str:
        """Gets the current target object."""
        return self._target_object

    @target_object.setter
    def target_object(self, new_target_object: str) -> None:
        """Sets a new target object and updates the status message."""
        with self._lock:
            self._target_object = new_target_object
        self.status_msg['target_object'] = f'Target: {self.target_object}'

    @property
    def current_controller(self):
        """Gets the current controller handling the robot's actions."""
        return self._current_controller

    @current_controller.setter
    def current_controller(self, new_controller) -> None:
        """Sets a new controller and updates the status message."""
        del self._current_controller
        self._current_controller = new_controller
        self.status_msg['controller'] = f'Controller: {self.current_controller.name}'

    def _update_state(self) -> None:
        """Updates the robot's state, including vision and controller selection."""
        self._update_vision()  # Update vision system

        with self._lock:
            curr_command = self.command

        curr_type = type(self.current_controller)

        # Command processing and controller switching
        if curr_command == 'goodbye':
            self.shutdown.set()
        elif curr_command == 'wait' and curr_type != StandbyController:
            self.current_controller = StandbyController(self)
        elif curr_command == 'pan' and curr_type != PanTiltController:
            self.current_controller = PanTiltController(self)
        elif curr_command == 'track' and curr_type != TrackController:
            self.current_controller = TrackController(self)
        elif curr_command == 'find':
            if curr_type != FindObjectController:
                self.current_controller = FindObjectController(self)
            elif self.current_controller.detection.is_set():
                with self._lock:
                    self.command = 'track'
        elif curr_command == 'drive' and curr_type != DriveTestController:
            self.current_controller = DriveTestController(self)

    def _update_vision(self) -> None:
        """Captures an image from the robot's camera and updates the vision status."""
        if self.robot.cap.isOpened():
            self.has_vision, self.image = self.robot.cap.read()
        else:
            self.has_vision = False

    def _update_robot(self) -> None:
        """Updates the robot's motion state based on supervisor control."""
        with self._lock:
            self.robot.pan = self.pan
            self.robot.tilt = self.tilt
            self.robot.v = self.v
            self.robot.omega = self.omega

        self.robot.update()  # Apply changes

    def _update_display(self) -> None:
        """Updates the robot's display with status messages and camera feed."""
        if self.has_vision:
            line_height = 15
            for i, key in enumerate(self.status_msg.keys()):
                cv2.putText(
                    self.image,
                    self.status_msg[key],
                    (10, line_height + i * line_height),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (255, 255, 255),
                    1,
                )

            cv2.imshow('robot_vision', self.image)
            self.robot.display.update(self.status_msg)

    def main(self) -> None:
        """Main loop for the Supervisor, handling state updates and control execution."""
        while not self.shutdown.is_set():
            self._update_state()  # Update state
            self.current_controller.update()  # Apply the current controller
            self._update_display()  # Update display output
            self._update_robot()  # Apply robot updates

            if cv2.waitKey(1) == 27:  # ESC key pressed
                break

        # Cleanup
        cv2.destroyAllWindows()
        del self.robot
        sys.exit(1)

    def listen_audio(self) -> None:
        """Starts listening for voice commands using an AI-based audio classifier."""
        audio.classify_audio(model=models.AUDIO_CLASSIFICATION_MODEL, callback=self.voice_input)

    def voice_input(self, label: str, score: float) -> bool:
        """
        Processes voice input from the AI-based classifier.

        Args:
            label: The recognized command label.
            score: The confidence score of the classification.

        Returns:
            bool: True to keep listening, False to stop.
        """
        if score < VOICE_CONFIDENCE_SCORE:
            return True

        label = label.split()[-1]  # Extract the last word of the label

        if label not in SUPPORTED_COMMANDS:
            return True

        with self._lock:
            self.command = label

        return label != 'goodbye'  # Stop listening if "goodbye" is detected

    def listen_cmd(self) -> None:
        """Listens for manual commands from user input."""
        while not self.shutdown.is_set():
            new_command = input("Enter command: ").split()

            if not new_command:
                continue

            if new_command[0] not in SUPPORTED_COMMANDS:
                continue

            with self._lock:
                self.command = new_command[0]
                if len(new_command) > 1:
                    self.target_object = ' '.join(new_command[1:])

    def execute(self) -> None:
        """Starts the supervisor's execution threads for command input and main control loop."""
        listen_thread = threading.Thread(target=self.listen_cmd, daemon=True)
        main_thread = threading.Thread(target=self.main)

        listen_thread.start()
        main_thread.start()
        main_thread.join()