import os

from Config import config
from Game import Game

add_library("minim")


g = None


def setup():
    size(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    # Loading from the sound libraries seems not work in other python files,
    # so we pass the Minim object to Game.
    soundPlayer = Minim(this)

    global g
    g = Game(soundPlayer)


def draw():
    if frameCount % 1 == 0:
        g.next_frame()
        g.display()


def keyPressed():
    g.handle_input(key, keyCode, True)


def keyReleased():
    g.handle_input(key, keyCode, False)
