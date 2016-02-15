import time
import math
import pigpio

# units
from pint import UnitRegistry
units = UnitRegistry()
units.define('steps = in / 254 = step')

DEFAULT_UNIT = units.parse_expression("steps")

def unit(val, **kw):
    _unit = kw.get("unit", DEFAULT_UNIT)
    if type(val) != units.Quantity:
        if type(val) in (int, float):
            assert _unit, "value %r of type '%r' requires a unit definition" % (val, type(val))
            val = val * _unit
        elif type(val) in (str, unicode):
            val = units.parse_expression(val)
        else:
            raise TypeError, "I don't know how to convert type '%s' to a unit" % str(type(val))
    assert type(val) == units.Quantity, "%r != %r" % (type(val), units.Quantity)
    if _unit:
        val = val.to(_unit)
    return val

def steps(val):
    val = unit(val)
    return int(val.to("steps").magnitude)

class CameraRail(object):
    pin_enable = 2
    pin_step = 3
    pin_dir = 4
    forward = 1
    backward = 0

    def __init__(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin_step, pigpio.OUTPUT)
        self.pi.set_mode(self.pin_dir, pigpio.OUTPUT)
        self.pi.set_mode(self.pin_enable, pigpio.OUTPUT)
        self._direction = self.forward
        self._position = 0
        self.pulse_len = 5
        self.enable = True
        self.speed = 100

    def set_zero(self, val=0):
        self._position = val

    def get_position(self):
        return self._position
    
    def set_position(self, pos):
        pos = steps(pos)
        self.move(pos)
    position = property(get_position, set_position)

    def get_relative(self):
        return 0

    def set_relative(self, pos):
        pos = steps(pos)
        self.move(self.position + pos)
    relative = property(get_relative, set_relative)

    def get_enable(self):
        return not bool(self._enable)

    def set_enable(self, value):
        self._enable = int(not bool(value))
        self.pi.write(self.pin_enable, self._enable)
    enable = property(get_enable, set_enable)

    def get_direction(self):
        return self._direction

    def set_direction(self, value):
        self._direction = int(bool(value))
        self.pi.write(self.pin_dir, self._direction)
        time.sleep(0.1)
    direction = property(get_direction, set_direction)

    def step(self):
        self.pi.gpio_trigger(self.pin_step, self.pulse_len, 1)
        if self.direction == self.forward:
            self._position += 1
        else:
            self._position -= 1

    def move(self, target):
        if self.position == target:
            return
        if self.position > target and self.direction == self.forward:
            self.direction = self.backward
        if self.position < target and self.direction == self.backward:
            self.direction = self.forward
        delay = 1.0 / self.speed
        while self.position != target:
            self.step()
            time.sleep(delay)

    def reverse():
        self.direction = not self.direction

class RailDirector(object):
    def __init__(self, rail):
        self.rail = rail
        self.steps_per_second = None
        self.start_ts = None
        self.distance = None
        self.time = None
        self._pause = False
        self.pause_ts = None

    def get_pause(self):
        return self._pause
    
    def set_pause(self, val):
        if self.start_ts:
            if val:
                self.pause_ts = time.time()
            elif self.pause_ts != None:
                self.start_ts += (self.pause_ts - self.start_ts)
                self.pause_ts = None
        self._pause = bool(val)
    pause = property(get_pause, set_pause)

    def schedule(self, distance, time):
        delta = unit(distance).magnitude
        self.distance = self.rail.position + int(math.floor(delta))
        self.time = unit(time, unit=units.parse_expression("seconds")).magnitude
        self.steps_per_second = self.distance / self.time
        self.start()

    def start(self):
        self.start_ts = time.time()
    
    def stop(self):
        self.start_ts = None

    def tick(self):
        if self.start_ts == None or (self.rail.position == self.distance):
            return False
        if not self.pause:
            delta = time.time() - self.start_ts
            position = self.steps_per_second * delta
            position = int(math.floor(position))
            if self.steps_per_second < 0:
                position = max(position, self.distance)
            else:
                position = min(position, self.distance)
            self.rail.position = position
        return True
