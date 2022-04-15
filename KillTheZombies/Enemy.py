import os
import random

import GUIManager as gui
from Config import config
from Entity import Entity
from Humanoid import Humanoid
from Pair import Pair
from Sprite import Sprite



class Enemy(Entity, Humanoid):
    def __init__(self, p0, p1, data):
        """
        p0: the top-left corner of the enemy on the screen
        p1: the bottom-right corner of the enemy on the screen
        """
        Entity.__init__(self, p0, p1, Sprite(
            loadImage(data["spritePath"]),
            data["spriteFrames"]
        ))
        Humanoid.__init__(self, data["health"])
        self.moveVector = Pair(data["speed"], data["speed"])
        self.damage = data["damage"]
        self.reward = data["reward"]


    def update(self, map, target, **kwargs):
        """Set velocity in order to move towards target, then move towards target."""
        self.velocity = Pair(0, 0)
        center = self.p0.midpoint(self.p1)
        
        dx = target.x - center.x
        if dx != 0:
            signDx = 1 if dx > 0 else -1
            moveX = dx if abs(dx) <= abs(self.moveVector.x) else signDx * self.moveVector.x
            self.velocity.x += moveX

        dy = target.y - center.y
        if dy != 0:
            signDy = 1 if dy > 0 else -1
            moveY = dy if abs(dy) <= abs(self.moveVector.y) else signDy * self.moveVector.y
            self.velocity.y += moveY
        
        # update sprite
        if dx == 0 and dy == 0:
            self.sprite.set_frame(0)
        elif abs(dx) > abs(dy):
            if dx > 0:
                self.sprite.set_frame(1)
            elif dx < 0:
                self.sprite.set_frame(2)
        elif abs(dy) > abs(dx):
            if dy > 0:
                self.sprite.set_frame(3)
            elif dy < 0:
                self.sprite.set_frame(4)
        
        considerWalls = kwargs.get("considerWalls", False)
        return Entity.update(self, map.grid, considerWalls=considerWalls)


    def __repr__(self):
        return "<Enemy p0={} p1={} hp={}>".format(self.p0, self.p1, self.health)



class Ghost(Enemy):
    def __init__(self, p0, p1, data=None):
        if data is None:
            data = config.ENEMY_DATA["Ghost"]

        Enemy.__init__(self, p0, p1, data)


    def update(self, map, target, **kwargs):
        return Enemy.update(self, map, target, considerWalls=False, **kwargs)



class Runner(Enemy):
    def __init__(self, p0, p1, data=None):
        if data is None:
            data = config.ENEMY_DATA["Runner"]

        Enemy.__init__(self, p0, p1, data)
        self.lastTarget = None


    def update(self, map, initialTarget, forceUseInitialTarget=False, forceUseLastTarget=False, **kwargs):
        """
        if forceUseInitialTarget, move towards initialTarget.
        if forceUseLastTarget, move towards lastTarget.
        Otherwise, if bfsDistance of the enemy > 0, move to an adjacent cell
        with a smaller bfsDistance.
        Otherwise, move towards initialTarget.
        """
        center = self.p0.midpoint(self.p1)
        cell = gui.screen_to_cell(center)
        target = initialTarget
        foundLastTarget = False

        if forceUseLastTarget and self.lastTarget is not None:
            target = self.lastTarget

        if (
            not forceUseInitialTarget
            and not forceUseLastTarget
            and map.bfsDistance[cell.x][cell.y] > 0
        ):
            cellDeltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            potentialTargets = []

            for dx, dy in cellDeltas:
                nextCell = cell + Pair(dx, dy)
                if (
                    map.bfsDistance[nextCell.x][nextCell.y] is not None
                    and map.bfsDistance[nextCell.x][nextCell.y] < map.bfsDistance[cell.x][cell.y]
                ):
                    nextp0 = gui.cell_to_screen(nextCell)
                    nextp1 = gui.cell_to_screen(nextCell) + self.size
                    potentialTarget = nextp0.midpoint(nextp1)
                    if (
                        self.lastTarget is not None
                        and potentialTarget.x == self.lastTarget.x
                        and potentialTarget.y == self.lastTarget.y
                    ):
                        target = potentialTarget
                        foundLastTarget = True
                        break
                    else:
                        potentialTargets.append(potentialTarget)
            
            if not foundLastTarget and len(potentialTargets) > 0:
                target = random.choice(potentialTargets)

        self.lastTarget = target
        return Enemy.update(self, map, target, **kwargs)



class Skipper(Runner):
    def __init__(self, p0, p1, data=None):
        if data is None:
            data = config.ENEMY_DATA["Skipper"]
            
        Runner.__init__(self, p0, p1, data)
        self.movingTime = 30
        self.restingTime = 40
        self.timer = 0
        # 0 = resting, 1 = moving
        self.status = 0


    def update(self, map, target, **kwargs):
        """Move towards target for a certain period of time, then rest for some time, then move again..."""
        if self.status == 0:
            # resting
            if self.timer > 0:
                self.timer -= 1
                return (False, False)
            else:
                # start moving
                self.status = 1
                self.timer = self.movingTime
        else:
            # moving
            if self.timer > 0:
                self.timer -= 1
            else:
                # stop moving
                self.status = 0
                self.timer = self.restingTime
                return (False, False)
        
        # move
        return Runner.update(self, map, target, **kwargs)


enemyTypes = [
    ("Ghost", Ghost),
    ("Runner", Runner),
    ("Skipper", Skipper)
]
