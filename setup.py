#!/usr/bin/env python

from setuptools import setup

sctk = {
    "name": "camrail",
    "description": "Python camera rail controller",
    "author":"Giles Hall",
    "author_email": "giles@polymerase.org",
    "packages": ["camrail"],
    "package_dir": {"camrail": "src"},
    "install_requires": [
        "pint", 
        "gphoto2",
        "flask",
        "mako",
        "flask-mako",
    ],
    "url": "https://github.com/vishnubob/camrail",
}

if __name__ == "__main__":
    setup(**sctk)
