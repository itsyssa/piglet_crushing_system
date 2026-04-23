import RPi.GPIO as GPIO
import time

RELAY_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

GPIO.output(RELAY_PIN, GPIO.LOW)   # ON (active-low relay)
print("SIREN ON")
time.sleep(0.3)

GPIO.output(RELAY_PIN, GPIO.HIGH)  # OFF
print("SIREN OFF")

GPIO.cleanup()
