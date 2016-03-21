import os
from flask import Flask, request, session, g, redirect, url_for, abort, flash, jsonify
from flask.ext.mako import MakoTemplates, render_template
import pickle
import camrail

ROOT_PATH = os.path.split(camrail.__file__)[0]
TEMPLATE_DIR = os.path.join(ROOT_PATH, "templates")

class Config(object):
    DEBUG = True
    TESTING = True
    MAKO_TRANSLATE_EXCEPTIONS = False
    template_folder = TEMPLATE_DIR

def bootstrap_server():
    app = Flask("camrail")
    config = Config()
    app.config.from_object(config)
    app.template_folder = config.template_folder
    mako_templates = MakoTemplates(app)
    globals()["app"] = app
    globals()["mako_templates"] = mako_templates

bootstrap_server()
camera = camrail.Camera()
rail = camrail.CameraRail()
#camera["main.imgsettings.imageformat"] = "RAW + Small Normal JPEG"
#camera["main.imgsettings.imageformat"] = "RAW"
director = None

OUTDIR = "/ginkgo/users/giles/code/camrail"

@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/start', methods=["POST"])
def start():
    global director
    if director != None and director.running:
        return get_status()
    info = request.json
    director = camrail.Director(info["interval"], info["step"], camera, rail, prefix=OUTDIR)
    director.start()
    return get_status()

@app.route('/stop', methods=["POST"])
def stop():
    global director
    if director != None:
        director.stop()
    director = None
    return get_status()

@app.route('/pause', methods=["POST"])
def pause():
    global director
    if director != None:
        director.pause = not director.pause
    return get_status()

@app.route('/thumbnail/preview.jpg')
def get_thumbnail():
    thumbnail = camera.get_thumbnail(refresh=True)
    return thumbnail

@app.route('/thumbnail/<image>')
def get_specific_thumbnail(image):
    image = os.path.join(OUTDIR, image)
    thumbnail = camera.get_thumbnail(filename=image)
    return thumbnail

@app.route('/status')
def get_status():
    global director
    if director == None:
        state = "stopped"
    elif not director.running:
        director = None
        state = "stopped"
    elif director.pause:
        state = "paused"
    else:
        state = "running"
    last_image = camera.last_image if camera.last_image else ""
    ret = {
        "position": rail.position,
        "state": state,
        "last_image": os.path.split(last_image)[-1],
        "stepper": "ON" if rail.enable else "OFF",
    }
    return jsonify(**ret)

@app.route('/set_home')
def set_home():
    rail.set_current_position()
    return get_status()

@app.route('/toggle_stepper')
def toggle_stepper():
    rail.enable = not rail.enable
    return get_status()

@app.route('/move', methods=["GET", "POST"])
def move():
    info = request.json
    print info
    rail.speed = int(info["speed"])
    pos = str(info["position"])
    if pos[0] == '@':
        pos = pos[1:]
        rail.position = pos
    else:
        rail.relative = pos
    return get_status()

cache_fn = os.path.join(os.path.expanduser("~"), ".camrail_cache")

def save_cache_state():
    info = {
        "position": rail.position
    }
    with open(cache_fn, 'wb') as fh:
        pickle.dump(info, fh)

def load_cache_state():
    global rail
    info = {
        "position": 0,
    }
    if os.path.exists(cache_fn):
        with open(cache_fn, 'rb') as fh:
            try:
                info = pickle.load(fh)
            except:
                pass
    rail.set_current_position(info["position"]) 

if __name__ == "__main__":
    app._static_folder = os.path.join(ROOT_PATH, "static")
    load_cache_state()
    try:
        app.run(host="0.0.0.0")
    finally:
        save_cache_state()
