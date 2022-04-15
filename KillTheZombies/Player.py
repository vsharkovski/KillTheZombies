import os

from Bullet import Bullet
from Config import config
from Entity import Entity
from Humanoid import Humanoid
from Pair import Pair
from Sprite import Sprite


class Player(Entity, Humanoid):
    def __init__(self, p0, p1, moveVector):
        Entity.__init__(self, p0, p1, Sprite(
            loadImage(os.path.join(config.PATH_ENTITIES, "soldier-32x.png")),
            8 # 4 images for shooting, 4 for not shooting
        ))
        Humanoid.__init__(self, config.PLAYER_HEALTH, config.PLAYER_DAMAGE_COOLDOWN)

        self.bulletSprite = Sprite(loadImage(os.path.join(config.PATH_ENTITIES, "bullet-32x.png")), 3)
        
        self.keyToSpriteDict = {
            config.KEYS["SHOOT_DOWN"]: 0,
            config.KEYS["SHOOT_UP"]: 1,
            config.KEYS["SHOOT_RIGHT"]: 2,
            config.KEYS["SHOOT_LEFT"]: 3,
            config.KEYS["MOVE_DOWN"]: 4,
            config.KEYS["MOVE_UP"]: 5,
            config.KEYS["MOVE_RIGHT"]: 6,
            config.KEYS["MOVE_LEFT"]: 7
        }
        
        self.moveVelocities = {
            config.KEYS["MOVE_LEFT"]: Pair(-moveVector.x, 0),
            config.KEYS["MOVE_RIGHT"]: Pair(moveVector.x, 0),
            config.KEYS["MOVE_UP"]: Pair(0, -moveVector.y),
            config.KEYS["MOVE_DOWN"]: Pair(0, moveVector.y)
        }
        
        self.bulletVelocities = {
            config.KEYS["SHOOT_LEFT"]: Pair(-config.BULLET_SPEED, 0),
            config.KEYS["SHOOT_RIGHT"]: Pair(config.BULLET_SPEED, 0),
            config.KEYS["SHOOT_UP"]: Pair(0, -config.BULLET_SPEED),
            config.KEYS["SHOOT_DOWN"]: Pair(0, config.BULLET_SPEED),
        }
        
        self.keyHandler = {}
        for direction in self.moveVelocities:
            self.keyHandler[direction] = False
        for direction in self.bulletVelocities:
            self.keyHandler[direction] = False

        self.money = 0
        self.damageLevel = 0
        self.piercingLevel = 0
        self.shotCooldownLevel = 0
        
        self.shotCooldownRemaining = 0
        self.queuedShots = []

        self.bulletMargin = Pair(config.BULLET_SIZE//2, config.BULLET_SIZE//2)


    def reset_input(self):
        """Stop all actions from the keyboard."""
        for d in self.keyHandler:
            self.keyHandler[d] = False


    def update(self, grid):
        """
        Update velocity if necessary keys are down,
        update position from velocity,
        queue shots if necessary keys are down.
        """
        if not self.alive:
            return
        
        self.velocity = Pair(0, 0)
        for direction in self.moveVelocities:
            if self.keyHandler[direction]:
                self.velocity += self.moveVelocities[direction]
                # update sprite, since moving
                self.sprite.frame = self.keyToSpriteDict[direction]
   
        for direction in self.bulletVelocities:
            if self.keyHandler[direction]:
                # shot cooldown need not be 0 to update sprite
                self.sprite.frame = self.keyToSpriteDict[direction]

        self.queuedShots = []
        if self.shotCooldownRemaining == 0:
            bulletVelocity = Pair(0, 0)
            for direction in self.bulletVelocities:
                if self.keyHandler[direction]:
                    bulletVelocity += self.bulletVelocities[direction]

            if bulletVelocity.x != 0 or bulletVelocity.y != 0:
                center = self.p0.midpoint(self.p1)
                self.queuedShots.append(Bullet(
                    self.p0,
                    self.p1,
                    self.bulletSprite,
                    bulletVelocity,
                    config.PLAYER_DAMAGE_VALUES[self.damageLevel],
                    config.PLAYER_PIERCING_VALUES[self.piercingLevel],
                    config.PLAYER_SHOT_COOLDOWN_VALUES[self.shotCooldownLevel]
                ))
                self.shotCooldownRemaining = config.PLAYER_SHOT_COOLDOWN_VALUES[self.shotCooldownLevel]
        
        self.shotCooldownRemaining = max(self.shotCooldownRemaining - 1, 0)

        return Entity.update(self, grid)


    def upgrade_damage(self):
        """Return True if successfully upgraded damage, and False otherwise."""
        if (
            self.damageLevel+1 >= len(config.PLAYER_DAMAGE_VALUES)
            or self.money < config.PLAYER_DAMAGE_PRICES[self.damageLevel+1]
        ):
            return False
        
        self.money -= config.PLAYER_DAMAGE_PRICES[self.damageLevel+1]
        self.damageLevel += 1
        return True


    def upgrade_shot_cooldown(self):
        """Return True if successfully upgraded shot cooldown, and False otherwise."""
        if (
            self.shotCooldownLevel+1 >= len(config.PLAYER_SHOT_COOLDOWN_VALUES)
            or self.money < config.PLAYER_SHOT_COOLDOWN_PRICES[self.shotCooldownLevel+1]
        ):
            return False
        
        self.money -= config.PLAYER_SHOT_COOLDOWN_PRICES[self.shotCooldownLevel+1]
        self.shotCooldownLevel += 1
        return True


    def upgrade_piercing(self):
        """Return True if successfully upgraded piercing, and False otherwise."""
        if (
            self.piercingLevel+1 >= len(config.PLAYER_PIERCING_VALUES)
            or self.money < config.PLAYER_PIERCING_PRICES[self.piercingLevel+1]
        ):
            return False
        
        self.money -= config.PLAYER_PIERCING_PRICES[self.piercingLevel+1]
        self.piercingLevel += 1
        return True


    def __repr__(self):
        return "<Player p0={} p1={} hp={}>".format(self.p0, self.p1, self.health)
