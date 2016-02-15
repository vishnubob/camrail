import os
from flask import Flask, request, session, g, redirect, url_for, abort, flash, jsonify
from flask.ext.mako import MakoTemplates, render_template
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
camera["main.imgsettings.imageformat"] = "RAW"
director = None

@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/start', methods=["POST"])
def start():
    global director
    if director != None and director.running:
        return get_status()
    info = request.json
    director = camrail.Director(camera, rail)
    director.rail_director.schedule(info["distance"], info["rate"])
    director.camera_director.schedule(int(info["interval"]))
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
    ret = {
        "position": rail.position,
        "state": state,
        "last_image": camera.last_image,
    }
    return jsonify(**ret)

@app.route('/set_home')
def set_home():
    rail.set_zero()
    ret = {
        "position": rail.position
    }
    return jsonify(**ret)


@app.route('/move', methods=["GET", "POST"])
def move():
    info = request.json
    rail.speed = int(info["speed"])
    try:
        rail.relative = int(info["step"])
    except:
        rail.relative = info["step"]
    return get_status()

if __name__ == "__main__":
    app._static_folder = os.path.join(ROOT_PATH, "static")
    app.run(host="0.0.0.0")
