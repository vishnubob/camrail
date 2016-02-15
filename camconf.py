import camrail
from pprint import pprint as pp
import time

cam = camrail.Camera()
cam.delete_all_files_on_camera()

cfg = cam.config
node = cfg.lookup("main.imgsettings.iso")
cam["settings.capturetarget"] = "Memory card"
cam["main.imgsettings.imageformat"] = "Small Normal JPEG"
#cam["main.actions.autofocusdrive"] = 1
#cam["main.actions.manualfocusdrive"] = "Far 3"
#node = cfg.lookup("capturesettings.exposurecompensation")
node = cfg.lookup("main.capturesettings.aperture")

for choice in node.choices:
    print choice
    node.value = choice
    if choice[0] == '-':
        choice = "neg_" + choice[1:]
    prefix = "%s_" % choice
    cam.capture(copy=True, prefix=prefix)

cam.delete_all_files_on_camera()
