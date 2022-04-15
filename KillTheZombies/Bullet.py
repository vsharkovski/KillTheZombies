import os
import random

from Config import config
from Entity import Entity


class Bullet(Entity):
    def __init__(self, p0, p1, sprite, velocity, damage, piercing, shotCooldown):
        Entity.__init__(self, p0, p1, sprite)
        self.velocity = velocity
        self.damage = damage
        self.piercing = piercing
        self.hitEntities = []
        self.broken = False
 

    def register_hit(self, entity):
        if (
            self.broken
            or len(self.hitEntities) >= self.piercing
            or entity in self.hitEntities
        ):
            return

        # print("{} hit {}".format(self, entity))
        self.hitEntities.append(entity)

        if len(self.hitEntities) >= self.piercing:
            self.broken = True


    def __repr__(self):
        return "<Bullet p0={} p1={} v={} dmg={}>".format(self.p0, self.p1, self.velocity, self.damage)
