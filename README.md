pibooth-twoflash
=================

`pibooth-twoflash` is a plugin for the [pibooth](https://pypi.org/project/pibooth) application.

It controls two independent LED outputs when the capture is taken.

Install
-------

```
pip3 install git+https://github.com/Nico31Fr/pibooth-twoflash.git
```
    

Configuration
-------------

Below are the new configuration options available in the [pibooth](https://pypi.org/project/pibooth) configuration. **The keys and their default values are automatically added to your configuration after first** [pibooth](https://pypi.org/project/pibooth) **restart.**

``` {.ini}
[FLASH]

# GPIO OUT pin for LED 1
led1_pin = 18
    
# GPIO OUT pin for LED 2
led2_pin = 12

# Duration of one complete crossfade cycle in milliseconds
crossfade_speed = 2000

# Maximum brightness of each LED during the crossfade, in percent
crossfade_max_brightness = 50

# Brightness of both LEDs during capture, in percent
capture_brightness = 100

```

Edit the configuration by running the command `pibooth --config`.


Circuit diagram
---------------

Here is the diagram for hardware connections.

![Electronic sketch](docs/images/sketch.png)
