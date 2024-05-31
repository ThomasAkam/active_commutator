import board
import pwmio
import touchio
import time
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn
from adafruit_motor import servo
from adafruit_dotstar import DotStar
from math import copysign

# Instantiate hardware ---------------------------

# Multicolour LED
pixel = DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# Red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Sensor
sensor = AnalogIn(board.D0)

# Servo
pwm = pwmio.PWMOut(board.D2, frequency=50)
motor = servo.ContinuousServo(pwm)

# Buttons
usr_button = touchio.TouchIn(board.D3)
startstop_button = touchio.TouchIn(board.D4)

# Parameters

neutral_value = 32800
start_threshold = 9000
stop_threshold = 3000
speed = 0.05
button_delay = 0.5


# Variables

moving = False


def detect_press():
    # Return whether one or both buttons are pressed.
    ss_pressed = startstop_button.value
    us_pressed = usr_button.value
    if ss_pressed or us_pressed:
        time.sleep(0.05)
        if startstop_button.value and usr_button.value:
            return "B"
        elif ss_pressed:
            return "S"
        elif us_pressed:
            return "U"


# Initial state

state = "running"
motor.throttle = 0
pixel[0] = (0, 255, 0)  # Set pixel Green

# Loop

while True:
    button_state = detect_press()
    value = sensor.value
    print("State:{} Sensor value: {} Moving: {}".format(state, value, moving))

    if state == "running":
        if button_state == "S":  # Stop running
            state = "stopped"
            moving = False
            motor.throttle = 0
            pixel[0] = (255, 0, 0)  # Set pixel red
            time.sleep(button_delay)
        else:  # Control motor
            diff = value - neutral_value
            if not moving and (abs(diff) > start_threshold) or moving and (abs(diff) > stop_threshold):
                moving = True
                motor.throttle = copysign(speed, diff)
                pixel[0] = (0, 0, 255)  # Set pixel blue
            else:
                motor.throttle = 0
                moving = False
                pixel[0] = (0, 255, 0)  # Set pixel green
            time.sleep(0.1)
    elif state == "stopped":  # Not running.
        if button_state == "S":  # start running
            state = "running"
            pixel[0] = (0, 255, 0)  # Set pixel green
            time.sleep(button_delay)
        elif button_state == "U":  # Reset neutral position.
            pixel[0] = (0, 0, 255)  # Set pixel blue
            neutral_value = sensor.value
            print(neutral_value)
            time.sleep(button_delay)
            pixel[0] = (255, 0, 0)  # Set pixel red
        else:
            time.sleep(0.1)
