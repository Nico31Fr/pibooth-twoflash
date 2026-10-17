    # -*- coding: utf-8 -*-

from math import cos, pi
from threading import Event, Thread
from time import monotonic
from gpiozero import PWMOutputDevice

import pibooth



__version__ = "1.2.0"



@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('FLASH', 'led1_pin', 12,
                   "GPIO OUT pin to light LED 1")
    cfg.add_option('FLASH', 'led2_pin', 13,
                   "GPIO OUT pin to light LED 2")
    cfg.add_option('FLASH', 'crossfade_speed', 2000,
                   "Duration of one complete LED crossfade cycle in milliseconds",
                   'Crossfade speed (ms)', [str(i) for i in range(500, 5001, 500)])
    cfg.add_option('FLASH', 'crossfade_max_brightness', 50,
                   "Maximum brightness of each LED during the crossfade, in percent",
                   'Crossfade max brightness (%)', [str(i) for i in range(0, 101, 10)])
    cfg.add_option('FLASH', 'capture_brightness', 100,
                   "Brightness of both LEDs during capture, in percent",
                   'Capture brightness (%)', [str(i) for i in range(0, 101, 10)])

@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Configure the two LED outputs."""
    app.pin_led1 = cfg.gettyped('FLASH', 'led1_pin')
    app.strip_led1 = PWMOutputDevice(app.pin_led1, frequency=100, initial_value=0)
    app.pin_led2 = cfg.gettyped('FLASH', 'led2_pin')
    app.strip_led2 = PWMOutputDevice(app.pin_led2, frequency=100, initial_value=0)
    app.crossfade_stop = None
    app.crossfade_thread = None

def _stop_crossfade(app):
    stop_event = getattr(app, 'crossfade_stop', None)
    thread = getattr(app, 'crossfade_thread', None)
    if stop_event is not None:
        stop_event.set()
    if thread is not None and thread.is_alive():
        thread.join()
    app.crossfade_stop = None
    app.crossfade_thread = None


def _crossfade(app, stop_event, speed, max_brightness):
    """Animate a smooth, complementary crossfade until capture starts."""
    period = max(speed, 1) / 1000.0
    started = monotonic()
    while not stop_event.is_set():
        phase = ((monotonic() - started) % period) / period
        # A cosine gives a smooth transition from LED 1 to LED 2 and back.
        led1 = max_brightness * (1 + cos(2 * pi * phase)) / 2
        led2 = max_brightness * (1 - cos(2 * pi * phase)) / 2
        app.strip_led1.value = led1 / 100
        app.strip_led2.value = led2 / 100
        stop_event.wait(0.02)


@pibooth.hookimpl
def state_preview_enter(cfg, app):
    """Crossfade both LEDs throughout the preview/countdown."""
    _stop_crossfade(app)
    stop_event = Event()
    app.crossfade_stop = stop_event
    app.crossfade_thread = Thread(
        target=_crossfade,
        args=(app, stop_event,
              cfg.gettyped('FLASH', 'crossfade_speed'),
              cfg.gettyped('FLASH', 'crossfade_max_brightness')),
        daemon=True)
    app.crossfade_thread.start()


@pibooth.hookimpl
def state_capture_enter(cfg, app):
    """Stop the crossfade and light both LEDs for the exposure."""
    _stop_crossfade(app)
    brightness = cfg.gettyped('FLASH', 'capture_brightness') / 100
    app.strip_led1.value = brightness
    app.strip_led2.value = brightness

@pibooth.hookimpl
def state_processing_enter(app, cfg):
    """Turn both LEDs off after the capture sequence."""
    _stop_crossfade(app)
    app.strip_led1.value = 0
    app.strip_led2.value = 0


@pibooth.hookimpl
def state_failsafe_enter(app):
    """Ensure the LEDs are off if pibooth enters its failsafe state."""
    _stop_crossfade(app)
    if hasattr(app, 'strip_led1'):
        app.strip_led1.value = 0
        app.strip_led2.value = 0


@pibooth.hookimpl
def pibooth_cleanup(app):
    """Stop animation and release GPIO resources on shutdown."""
    if hasattr(app, 'strip_led1'):
        _stop_crossfade(app)
        app.strip_led1.value = 0
        app.strip_led2.value = 0
        app.strip_led1.close()
        app.strip_led2.close()
