#!/usr/bin/env python

import rail
import camera
import time
import threading

class Director(threading.Thread):
    def __init__(self, _camera, _rail):
        super(Director, self).__init__()
        self.camera = _camera
        self.rail = _rail
        self.camera_director = camera.CameraDirector(self.camera)
        self.rail_director = rail.RailDirector(self.rail)
        self.daemon = True
        self.running = False

    def tick(self):
        if self.camera_director.tick():
            return True
        return self.rail_director.tick()

    def get_pause(self):
        return self.rail_director.pause
    
    def set_pause(self, val):
        self.camera_director.pause = val
        self.rail_director.pause = val
    pause = property(get_pause, set_pause)

    def stop(self):
        self.running = False
        self.join()

    def run(self):
        self.camera_director.start()
        self.rail_director.start()
        self.running = True
        while self.running:
            time.sleep(.01)
            if not self.camera_director.pretrigger():
                continue
            if not self.tick():
                break
        self.running = False
