import RPi.GPIO as gpio          

class Motor():
    def __init__(self, motor_pins):
        # assing pin numbers
        self.enable = motor_pins[0]
        self.in1 = motor_pins[1]
        self.in2 = motor_pins[2]

        # gpio setup
        gpio.setmode(gpio.BCM)
        gpio.setup(self.in1,gpio.OUT)
        gpio.setup(self.in2,gpio.OUT)
        gpio.setup(self.enable,gpio.OUT)

        # default values
        gpio.output(self.in1,gpio.LOW)
        gpio.output(self.in2,gpio.LOW)

        # PWM setup
        self.pwm = gpio.PWM(self.enable, 1000)
        self.pwm.start(0)

    def __del__(self):
        self.pwm.stop()
        gpio.cleanup()

    def run(self, speed):
        speed = max(min(speed, 100.0), -100.0)
        self.pwm.ChangeDutyCycle(abs(speed))

        # stop
        if speed == 0:
            gpio.output(self.in1,gpio.LOW)
            gpio.output(self.in2,gpio.LOW)

        # forward
        elif speed > 0:
            gpio.output(self.in1,gpio.HIGH)
            gpio.output(self.in2,gpio.LOW)

        # backward
        else:
            gpio.output(self.in1,gpio.LOW)
            gpio.output(self.in2,gpio.HIGH)
