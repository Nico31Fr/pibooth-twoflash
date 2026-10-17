    # -*- coding: utf-8 -*-

from time import sleep
from gpiozero import PWMOutputDevice

import pibooth
from pibooth.utils import LOGGER



__version__ = "1.2.0"



@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('FLASH', 'warmwhite_pin', 12,
                   "Physical GPIO OUT pin to light a warm white LED strip")
    cfg.add_option('FLASH', 'coolwhite_pin', 13,
                   "Physical GPIO OUT pin to light a cool white LED strip")
    cfg.add_option('FLASH', 'white_balance', (50, 50),
                   "The white balance (warm white, cool white) in percent",
                   'White balance (warm, cool)', [str((i, 100 - i)) for i in range(10, 100, 10)])
    cfg.add_option('FLASH', 'brightness', 50,
                   "The brightness in percent",
                   'Brightness (%)', [str(i) for i in range(0, 101, 10)])
    cfg.add_option('FLASH', 'fade_delay', 1000,
                   "How long is the fade light in milliseconds (0 to skip it)",
                   'Fade delay (ms)', [str(i) for i in range(0, 2001, 100)])

@pibooth.hookimpl
def state_chosen_exit(app, cfg):
    """Configure LED strips (warm white and cool white).
    """
    app.pin_warmwhite = cfg.gettyped('FLASH', 'warmwhite_pin')
    app.strip_warmwhite = PWMOutputDevice(app.pin_warmwhite, frequency=100, initial_value=0)

    app.pin_coolwhite = cfg.gettyped('FLASH', 'coolwhite_pin')
    app.strip_coolwhite = PWMOutputDevice(app.pin_coolwhite, frequency=100, initial_value=0)

    """Turn on the flash.
    """
    white_balance = cfg.gettyped('FLASH', 'white_balance')
    brightness = cfg.gettyped('FLASH', 'brightness')
    fade_delay = cfg.gettyped('FLASH', 'fade_delay')

    if fade_delay != 0:
        level_warmwhite = 0
        level_coolwhite = 0

        steps_number = fade_delay / 10
        step_warmwhite = white_balance[0] / steps_number
        step_coolwhite = white_balance[1] / steps_number

        while level_warmwhite <= white_balance[0] and level_coolwhite <= white_balance[1]:
            app.strip_warmwhite.value = level_warmwhite * brightness / 10000
            app.strip_coolwhite.value = level_coolwhite * brightness / 10000

            sleep(10 / 1000)

            level_warmwhite += step_warmwhite
            level_coolwhite += step_coolwhite

    app.strip_warmwhite.value = white_balance[0] * brightness / 10000
    app.strip_coolwhite.value = white_balance[1] * brightness / 10000

@pibooth.hookimpl
def state_processing_enter(app, cfg):
    """Turn off the flash.
    """
    white_balance = cfg.gettyped('FLASH', 'white_balance')
    brightness = cfg.gettyped('FLASH', 'brightness')
    fade_delay = cfg.gettyped('FLASH', 'fade_delay')

    if fade_delay != 0:
        level_warmwhite = white_balance[0]
        level_coolwhite = white_balance[1]

        steps_number = fade_delay / 10
        step_warmwhite = white_balance[0] / steps_number
        step_coolwhite = white_balance[1] / steps_number

        while level_warmwhite >= 0 and level_coolwhite >= 0:
            app.strip_warmwhite.value = level_warmwhite * brightness / 10000
            app.strip_coolwhite.value = level_coolwhite * brightness / 10000

            sleep(10 / 1000)

            level_warmwhite -= step_warmwhite
            level_coolwhite -= step_coolwhite

    app.strip_warmwhite.value = 0
    app.strip_coolwhite.value = 0

    """Stop LED strips (warm white and cool white).
    """
    app.strip_warmwhite.close()
    app.strip_coolwhite.close()
