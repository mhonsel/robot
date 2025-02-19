import cv2
import sys
import threading
import time

from aiymakerkit import audio

# local imports
import data.models as models
from controllers.standby_controller import StandbyController
from controllers.pan_tilt_controller import PanTiltController
from controllers.track_controller import TrackController
from controllers.find_object_controller import FindObjectController
from controllers.drive_test_controller import DriveTestController

VOICE_CONFIDENCE_SCORE = 0.5
SUPPORTED_COMMANDS = ('wait', 'drive', 'track', 'find', 'goodbye')


class Supervisor:
    def __init__(self, robot):
        self.robot = robot

        # threading
        self._lock = threading.RLock()
        self.shutdown = threading.Event()

        # state machine
#        self.state = SupervisorState(self)

        # initial state
        self.pan = 0.0
        self.tilt = 0.0
        self.v = 0.0
        self.omega = 0.0
        self._command = 'wait'
        self._target_object = ''

        # controllers
        self._current_controller = StandbyController(self) 

        # initialize vision
        self._update_vision()

        # status msg
        self.status_msg = {
                'command': 'Command: {}'.format(self.command),
                'target_object': 'Target: {}'.format(self.target_object),
                'controller': 'Controller: {}'.format(self.current_controller.name)
                }


    @property
    def command(self):
        return self._command


    @command.setter
    def command(self, new_command):
        with self._lock:
            self._command = new_command
        self.status_msg['command'] = 'Command: {}'.format(self.command)


    @property
    def target_object(self):
        return self._target_object


    @target_object.setter
    def target_object(self, new_target_object):
        with self._lock:
            self._target_object = new_target_object
        self.status_msg['target_object'] = 'Target: {}'.format(self.target_object)


    @property
    def current_controller(self):
        return self._current_controller


    @current_controller.setter
    def current_controller(self, new_controller):
        del self._current_controller
        self._current_controller = new_controller
        self.status_msg['controller'] = 'Controller: {}'.format(self.current_controller.name)


    # update supervisor and control state
    def _update_state(self):
        # update vision 
        self._update_vision()

        # calculate new controller outputs
#       self._update_controllers()

        # update the control state
#       self.state.update()
        with self._lock:
            curr_command = self.command

        curr_type = type(self.current_controller)
        if curr_command == 'goodbye':
            self.shutdown.set()
        elif curr_command == 'wait':
            if curr_type != StandbyController:
                self.current_controller = StandbyController(self)
        elif curr_command == 'pan':
            if curr_type != PanTiltController:
                self.current_controller = PanTiltController(self)
        elif curr_command == 'track':
            if curr_type != TrackController:
                self.current_controller = TrackController(self)
        elif curr_command == 'find':
            if curr_type != FindObjectController:
                self.current_controller = FindObjectController(self)
            elif self.current_controller.detection.is_set():
                with self._lock:
                    self.command = 'track'
        elif curr_command == 'drive':
            if curr_type != DriveTestController:
                self.current_controller = DriveTestController(self)


    def _update_vision(self):
        if self.robot.cap.isOpened():
            self.has_vision, self.image = self.robot.cap.read()
#            if self.has_vision:
#                self.image = cv2.flip(self.image, 0)

        else:
            self.has_vision = False


    def _update_robot(self):
        # update robot target state
        with self._lock:
            self.robot.pan = self.pan
            self.robot.tilt = self.tilt
            self.robot.v = self.v
            self.robot.omega = self.omega

        # update robot
        self.robot.update()


    def _update_display(self):
        if self.has_vision:
            # status display
            line_height = 15
            for i, key in enumerate(self.status_msg.keys()):
                cv2.putText(self.image, self.status_msg[key], (10, line_height + i * line_height), 
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

            # show image
            cv2.imshow('robot_vision', self.image)

            # update robot display
            self.robot.display.update(self.status_msg)
        

    def main(self):
        while not self.shutdown.is_set():
            self._update_state()  # update state
            self.current_controller.update()  # apply the current controller
            self._update_display() # show the view of the robot
            self._update_robot()  # update the robot with the output of the supervisor

            if cv2.waitKey(1) == 27: # ESC key
                break
        # cleanup
        cv2.destroyAllWindows()
        del self.robot
        sys.exit(1)


    def listen_audio(self):
        audio.classify_audio(model=models.AUDIO_CLASSIFICATION_MODEL, callback=self.voice_input)


    def voice_input(self, label, score):
        # Only use matches with higher confidence score
        if score < VOICE_CONFIDENCE_SCORE:
            return True

        label = label.split()[-1]
        
        # Only use valid voice commands
        if label not in SUPPORTED_COMMANDS:
            return True
        
#        print('CALLBACK: ', label, '=>', score)

        with self._lock:
            self.command = label

        if label == 'goodbye':
            return False

        return True  # keep listening
    

    def listen_cmd(self):
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
            

    def execute(self):
        listen_thread = threading.Thread(target=self.listen_cmd, daemon=True)
        main_thread = threading.Thread(target=self.main)
        listen_thread.start()
        main_thread.start()
        main_thread.join()
