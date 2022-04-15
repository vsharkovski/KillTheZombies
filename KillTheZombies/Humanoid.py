from Config import config



class Humanoid:
    def __init__(self, health, damageCooldown=0):
        self.maxHealth = health
        self.health = health
        self.alive = True
        self.damageCooldown = damageCooldown
        self.damageCooldownRemaining = 0


    def take_damage(self, damage):
        if self.damageCooldownRemaining == 0:
            self.damageCooldownRemaining = self.damageCooldown

            self.health -= damage
            if self.health <= 0:
                self.alive = False
                self.health = 0

        self.damageCooldownRemaining = max(self.damageCooldownRemaining - 1, 0)


    def heal(self):
        self.alive = True
        self.health = self.maxHealth
