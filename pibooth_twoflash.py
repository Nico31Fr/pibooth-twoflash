    # -*- coding: utf-8 -*-

from threading import Event, Thread
from time import monotonic
from gpiozero import PWMOutputDevice

import pibooth



__version__ = "1.2.0"



@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('FLASH', 'led1_pin', 18,
                   "GPIO OUT pin to light LED 1")
    cfg.add_option('FLASH', 'led2_pin', 19,
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
    cfg.add_option('FLASH', 'preflash_lead', 1000,
                   "Time before the end of the countdown when both LEDs light up at capture brightness, in milliseconds",
                   'Pre-flash lead time (ms)', [str(i) for i in range(0, 3001, 250)])
    cfg.add_option('FLASH', 'animation', 'swing',
                   "LED animation during the countdown: 'swing' (one LED after the other) "
                   "or 'fade' (both LEDs fading together)",
                   'Animation', ['swing', 'fade'])

@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Configure the two LED outputs."""
    app.pin_led1 = cfg.gettyped('FLASH', 'led1_pin')
    app.strip_led1 = PWMOutputDevice(app.pin_led1, frequency=200, initial_value=0)
    app.pin_led2 = cfg.gettyped('FLASH', 'led2_pin')
    app.strip_led2 = PWMOutputDevice(app.pin_led2, frequency=200, initial_value=0)
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


def _swing(phase, max_brightness):
    """Fade LED 1 out, LED 2 in and out, then LED 1 back in.

    The inactive LED stays at zero throughout each ramp, so the outputs never
    overlap.
    """
    if phase < 0.25:
        return max_brightness * (1 - phase * 4), 0
    if phase < 0.5:
        return 0, max_brightness * (phase - 0.25) * 4
    if phase < 0.75:
        return 0, max_brightness * (1 - (phase - 0.5) * 4)
    return max_brightness * (phase - 0.75) * 4, 0


def _fade(phase, max_brightness):
    """Fade both LEDs in and out together."""
    if phase < 0.5:
        value = max_brightness * phase * 2
    else:
        value = max_brightness * (1 - (phase - 0.5) * 2)
    return value, value


def _animate(app, stop_event, speed, max_brightness, preflash_at,
             capture_brightness, shape):
    """Animate both LEDs until the pre-flash, then hold the capture light."""
    period = max(speed, 1) / 1000.0
    started = monotonic()
    while not stop_event.is_set():
        elapsed = monotonic() - started
        if elapsed >= preflash_at:
            # Both LEDs stay at capture brightness so the camera exposure is
            # measured under the same light as the capture.
            app.strip_led1.value = capture_brightness
            app.strip_led2.value = capture_brightness
            return
        phase = (elapsed % period) / period
        led1, led2 = shape(phase, max_brightness)
        app.strip_led1.value = led1 / 100
        app.strip_led2.value = led2 / 100
        stop_event.wait(0.02)


@pibooth.hookimpl
def state_preview_enter(cfg, app):
    """Animate both LEDs during the countdown, then pre-flash before the capture."""
    _stop_crossfade(app)
    stop_event = Event()
    app.crossfade_stop = stop_event
    preflash_at = max(cfg.getint('WINDOW', 'preview_delay') - cfg.getint('FLASH', 'preflash_lead') / 1000, 0)
    animation = cfg.gettyped('FLASH', 'animation')
    app.crossfade_thread = Thread(
        target=_animate,
        args=(app, stop_event,
              cfg.gettyped('FLASH', 'crossfade_speed'),
              cfg.gettyped('FLASH', 'crossfade_max_brightness'),
              preflash_at,
              cfg.gettyped('FLASH', 'capture_brightness') / 100,
              _fade if animation == 'fade' else _swing),
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
