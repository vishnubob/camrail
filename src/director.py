#!/usr/bin/env python

import rail
import camera
import time
import threading
import logging

class Director(threading.Thread):
    def __init__(self, interval, step, _camera, _rail, prefix=""):
        super(Director, self).__init__()
        self.camera = _camera
        self.rail = _rail
        self.interval = float(interval)
        self.step = step
        self._pause = False
        self.daemon = True
        self.running = False
        self.prefix = prefix

    def get_pause(self):
        self._pause
    
    def set_pause(self, val):
        self._pause = val
        if self._pause:
            self._pause_ts = time.time()
        else:
            delta = max(0, self._pause_ts - self.next_event)
            self.next_event = time.time() + delta
    pause = property(get_pause, set_pause)

    def stop(self):
        self.running = False
        self.join()

    def trigger(self):
        now = time.time()
        self.next_event = now + self.interval
        pos = self.rail.position
        fn = self.camera.capture(copy=True, prefix=self.prefix)
        msg = "%s: Captured %s at step %s\n" % (time.strftime("%c"), fn, pos)
        with open("camrail.txt", 'a') as fh:
            fh.write(msg)
        self.camera.delete_all_files_on_camera()
        self.rail.relative = self.step

    def run(self):
        self.running = True
        self.start_ts = time.time()
        self.trigger()
        while self.running:
            if not self.pause:
                if time.time() > self.next_event:
                    self.trigger()
            time.sleep(.01)
