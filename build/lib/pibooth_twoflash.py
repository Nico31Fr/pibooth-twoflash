    # -*- coding: utf-8 -*-

from time import sleep
from gpiozero import PWMOutputDevice

import pibooth
from pibooth.utils import LOGGER



__version__ = "1.2.0"



@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('FLASH', 'led1_pin', 12,
                   "GPIO OUT pin to light LED 1")
    cfg.add_option('FLASH', 'led2_pin', 13,
                   "GPIO OUT pin to light LED 2")
    cfg.add_option('FLASH', 'led1_brightness', 50,
                   "LED 1 brightness in percent",
                   'LED 1 brightness (%)', [str(i) for i in range(0, 101, 10)])
    cfg.add_option('FLASH', 'led2_brightness', 50,
                   "LED 2 brightness in percent",
                   'LED 2 brightness (%)', [str(i) for i in range(0, 101, 10)])
    cfg.add_option('FLASH', 'fade_delay', 1000,
                   "How long is the fade light in milliseconds (0 to skip it)",
                   'Fade delay (ms)', [str(i) for i in range(0, 2001, 100)])

@pibooth.hookimpl
def state_chosen_exit(app, cfg):
    """Configure LED outputs and turn them on."""
    app.pin_led1 = cfg.gettyped('FLASH', 'led1_pin')
    app.strip_led1 = PWMOutputDevice(app.pin_led1, frequency=100, initial_value=0)

    app.pin_led2 = cfg.gettyped('FLASH', 'led2_pin')
    app.strip_led2 = PWMOutputDevice(app.pin_led2, frequency=100, initial_value=0)

    brightness_led1 = cfg.gettyped('FLASH', 'led1_brightness')
    brightness_led2 = cfg.gettyped('FLASH', 'led2_brightness')
    fade_delay = cfg.gettyped('FLASH', 'fade_delay')

    if fade_delay != 0:
        steps_number = max(1, int(fade_delay / 10))
        for step in range(1, steps_number + 1):
            app.strip_led1.value = brightness_led1 * step / (100 * steps_number)
            app.strip_led2.value = brightness_led2 * step / (100 * steps_number)
            sleep(0.01)

    app.strip_led1.value = brightness_led1 / 100
    app.strip_led2.value = brightness_led2 / 100

@pibooth.hookimpl
def state_processing_enter(app, cfg):
    """Fade out and close the LED outputs."""
    brightness_led1 = cfg.gettyped('FLASH', 'led1_brightness')
    brightness_led2 = cfg.gettyped('FLASH', 'led2_brightness')
    fade_delay = cfg.gettyped('FLASH', 'fade_delay')

    if fade_delay != 0:
        steps_number = max(1, int(fade_delay / 10))
        for step in range(steps_number - 1, -1, -1):
            app.strip_led1.value = brightness_led1 * step / (100 * steps_number)
            app.strip_led2.value = brightness_led2 * step / (100 * steps_number)
            sleep(0.01)

    app.strip_led1.value = 0
    app.strip_led2.value = 0
    app.strip_led1.close()
    app.strip_led2.close()
