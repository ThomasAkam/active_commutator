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

# Variables

running = False
proportional = True
button_delay = 0.3
neutral_value = sensor.value
threshold = 5000
gain = 1e-5   # Used in proportional mode only
speed = 0.04  # Used in non-proportional model only

# Loop

pixel[0] = (255,0,0) # Set pixel red

while True:
    if running:
        if startstop_button.value: # Stop running
            running = False
            motor.throttle = 0
            pixel[0] = (255,0,0) # Set pixel red
            time.sleep(button_delay)
        else: # Control motor
            value = sensor.value
            diff = value-neutral_value
            if abs(diff) > threshold:
                if proportional:
                    motor.throttle = diff*gain
                else:
                    motor.throttle = copysign(speed, diff)
            else:
                motor.throttle = 0
            time.sleep(0.01)
    else: # Not running.
        if startstop_button.value: # start running
            running = True
            pixel[0] = (0,255,0) # Set pixel green
            time.sleep(button_delay)
        elif usr_button.value: # Reset neutral position.
            pixel[0] = (0,0,255) # Set pixel blue
            neutral_value = sensor.value
            print(neutral_value)
            time.sleep(button_delay)
            pixel[0] = (255,0,0) # Set pixel red 


