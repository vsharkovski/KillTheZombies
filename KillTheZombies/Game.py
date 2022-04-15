import glob
import os
import random

import GUIManager as gui
from Bullet import Bullet
from Config import config
from Enemy import enemyTypes
from Entity import Entity
from Humanoid import Humanoid
from Map import Map
from Pair import Pair
from Player import Player
from Sprite import Sprite



class Game:
    def __init__(self, soundPlayer):
        self.maximumLevelReached = 0
        self.status = None
        self.drewWalls = False

        # load sprites
        self.decorationSprites = []
        for filename in glob.glob(os.path.join(config.PATH_DECORATIONS, "*-25x.png")):
            self.decorationSprites.append(Sprite(loadImage(filename)))
        
        # load sounds
        self.backgroundMusic = soundPlayer.loadFile(os.path.join(config.PATH_SOUNDS, "Background.mp3"))
        self.backgroundMusic.setGain(-15)
        self.backgroundMusic.loop()
    
        self.shootSound = soundPlayer.loadFile(os.path.join(config.PATH_SOUNDS, "Gunshot.mp3"))
        self.shootSound.setGain(-25)
        
        self.bulletHitSound = soundPlayer.loadFile(os.path.join(config.PATH_SOUNDS, "Bullet Hit.wav"))
        self.bulletHitSound.setGain(-25)

        self.playerHitSound = soundPlayer.loadFile(os.path.join(config.PATH_SOUNDS, "Grunt 1.mp3"))
        self.playerHitSound.setGain(-15)
        
        self.enemyDeathSounds = []
        for path, gain in [
            ("Grunt 2.wav", -12),
            ("Grunt 3.wav", -12),
            ("Grunt 4.wav", -12)
        ]:
            file = soundPlayer.loadFile(os.path.join(config.PATH_SOUNDS, path))
            if file is not None:
                file.setGain(gain)
                self.enemyDeathSounds.append(file)

        self.purchaseSound = soundPlayer.loadFile(os.path.join(config.PATH_SOUNDS, "Purchase.wav"))
        self.purchaseSound.setGain(-20)

        self.go_to_menu()


    def go_to_menu(self):
        """Go to the menu."""
        self.status = config.STATUS_MENU
    

    def go_to_end(self):
        """End the game."""
        self.status = config.STATUS_ENDED


    def go_to_shop(self):
        """Go to the shop."""
        self.status = config.STATUS_SHOP


    def start(self):
        """Start the game."""
        self.levelStartTimer = None
        self.deathTimer = None
        self.firstFrameOfLevel = None

        self.level = 0
        self.enemies = []
        self.bullets = []
        self.map = Map(self.decorationSprites)

        self.entityMargin = Pair(config.ENTITY_MARGIN, config.ENTITY_MARGIN)
        self.entitySize = (
            gui.cell_to_screen(Pair(1, 1))
            - gui.cell_to_screen(Pair(0, 0))
            - Pair(1, 1)
            - self.entityMargin
            - self.entityMargin
        )
        # print("entitySize={}".format(self.entitySize))

        self.player = Player(
            Pair(0, 0),
            Pair(0, 0) + self.entitySize,
            Pair(config.PLAYER_SPEED, config.PLAYER_SPEED)
        )
        
        self.start_level()


    def start_level(self):
        """Start a new level."""
        self.status = config.STATUS_PLAYING

        self.level += 1
        self.maximumLevelReached = max(self.level, self.maximumLevelReached)
        self.enemies = []
        self.bullets = []

        self.map.generate_walls()
        self.map.generate_decorations()
        playerStartCell = self.map.get_random_cell(config.CELL_EMPTY)

        # spawn the player
        self.player.reset_input()
        self.player.heal()
        self.player.teleport(gui.cell_to_screen(playerStartCell) + self.entityMargin)

        # spawn the enemies
        self.map.run_bfs(playerStartCell)

        potentialCells = []
        for x in range(config.GRID_COLS):
            for y in range(config.GRID_ROWS):
                if self.map.grid[x][y] == config.CELL_EMPTY:
                    if self.map.bfsDistance[x][y] >= config.ENEMY_MIN_SPAWN_DISTANCE:
                        potentialCells.append(Pair(x, y))
        
        numEnemies = ceil(
            config.BASE_ENEMY_NUMBER * (1 + config.K_ENEMY_NUMBER * self.level)
        )

        for i in range(numEnemies):
            cell = random.choice(potentialCells)
            cellOnScreen = gui.cell_to_screen(cell)
            enemyName, enemyClass = random.choice(enemyTypes)
            self.enemies.append(enemyClass(
                cellOnScreen + self.entityMargin,
                cellOnScreen + self.entityMargin + self.entitySize,
            ))
        
        self.levelStartTimer = config.LEVEL_START_WAIT_TIME
        self.levelBeatenTimer = None
        self.deathTimer = None
        self.firstFrameOfLevel = True


    def handle_input(self, key, key_code, is_down):
        """Handle input from the keyboard."""
        key = str(key).lower()
        # print("Pressed key={} keyCode={} status={}".format(key, key_code, is_down))

        if self.status == config.STATUS_MENU:
            if is_down and triple_compare(key, key_code, config.KEYS["CONTINUE"]):
                self.start()

        elif self.status == config.STATUS_PLAYING:
            if key_code in self.player.keyHandler:
                self.player.keyHandler[key_code] = is_down
            elif key in self.player.keyHandler:
                self.player.keyHandler[key] = is_down

        elif self.status == config.STATUS_SHOP:
            if not is_down:
                return

            if triple_compare(key, key_code, config.KEYS["CONTINUE"]):
                self.start_level()
            elif triple_compare(key, key_code, config.KEYS["SHOP_UPGRADE_DAMAGE"]):
                if self.player.upgrade_damage():
                    self.purchaseSound.play(0)
            elif triple_compare(key, key_code, config.KEYS["SHOP_UPGRADE_SHOT_COOLDOWN"]):
                if self.player.upgrade_shot_cooldown():
                    self.purchaseSound.play(0)
            elif triple_compare(key, key_code, config.KEYS["SHOP_UPGRADE_PIERCING"]):
                if self.player.upgrade_piercing():
                    self.purchaseSound.play(0)

        elif self.status == config.STATUS_ENDED:
            if is_down and triple_compare(key, key_code, config.KEYS["CONTINUE"]):
                self.go_to_menu()


    def display(self):
        """Display the game on the screen."""
        if self.status == config.STATUS_MENU:
            gui.draw_title(self.maximumLevelReached)
        elif self.status == config.STATUS_PLAYING:
            gui.draw_game_area(
                self.map,
                self.player,
                self.enemies,
                self.bullets,
                self.firstFrameOfLevel
            )
            gui.draw_info(
                self.player.health,
                self.player.maxHealth,
                self.player.money,
                self.level
            )
            self.drewWalls = True
        elif self.status == config.STATUS_SHOP:
            gui.draw_shop(
                self.player.money,
                self.player.damageLevel,
                self.player.shotCooldownLevel,
                self.player.piercingLevel
            )
        elif self.status == config.STATUS_ENDED:
            gui.draw_game_over(self.level)


    def next_frame(self):
        """Do the logic for the next frame."""
        if self.status == config.STATUS_MENU:
            pass
        
        elif self.status == config.STATUS_PLAYING:
            self.next_frame_game()

        elif self.status == config.STATUS_SHOP:
            pass
        
        elif self.status == config.STATUS_ENDED:
            pass

        
    def next_frame_game(self):
        """Do the logic for the next frame while playing a level."""
        # timers to make the transitions between scenest not as jarring
        if self.levelStartTimer is not None:
            if self.levelStartTimer == 0:
                self.levelStartTimer = None
            else:
                self.levelStartTimer -= 1
                return

        elif self.levelBeatenTimer is not None:
            if self.levelBeatenTimer == 0:
                self.go_to_shop()
                return
            else:
                self.levelBeatenTimer -= 1

        elif self.deathTimer is not None:
            if self.deathTimer == 0:
                self.go_to_end()
                return
            else:
                self.deathTimer -= 1      

        # Move the player
        self.player.update(self.map.grid)

        # Shoot new bullets
        shotOnce = False
        for bullet in self.player.queuedShots:
            # print("Spawning {}".format(bullet))
            self.bullets.append(bullet)
            if not shotOnce:
                shotOnce = True
                self.shootSound.play(0)

        # Move bullets, damage enemies
        remainingBullets = []
        for bullet in self.bullets:
            didMove = bullet.update(self.map.grid)
            if not didMove[0] or not didMove[1]:
                continue

            keepBullet = True
            for enemy in self.enemies:
                _, _, newx, newy = bullet.is_colliding(enemy)
                if newx and newy:
                    # print("{} collided with {}, removing".format(bullet, enemy))
                    enemy.take_damage(bullet.damage)
                    self.bulletHitSound.play(0)
                    if not enemy.alive and len(self.enemyDeathSounds) > 0:
                        deathSound = random.choice(self.enemyDeathSounds)
                        deathSound.play(0)

                    bullet.register_hit(enemy)
                    if bullet.broken:
                        keepBullet = False

                    break

            if keepBullet:
                remainingBullets.append(bullet)
    
        self.bullets = remainingBullets
        
        # Move the enemies
        remainingEnemies = []

        playerCenter = self.player.p0.midpoint(self.player.p1)
        playerCell = gui.screen_to_cell(playerCenter)
        self.map.run_bfs(playerCell)

        for enemy in self.enemies:
            if not enemy.alive:
                # The enemy was killed.
                self.player.money += enemy.reward
                # Ignore it when it comes to collision with the player,
                # since it will be removed anyway for the next frame.
                continue

            if self.player.alive:
                enemy.update(self.map, playerCenter)
                _, _, newx, newy = self.player.is_colliding(enemy)

                if newx and newy:
                    # The enemy is touching the player.
                    self.player.take_damage(enemy.damage)
                    if not self.playerHitSound.isPlaying():
                        self.playerHitSound.play(0)
                    if not self.player.alive:
                        self.deathTimer = config.PLAYER_DEATH_WAIT_TIME
        
            else:
                enemy.update(
                    self.map,
                    gui.cell_to_screen(Pair(
                        random.randint(0, config.GRID_COLS-1),
                        random.randint(0, config.GRID_ROWS-1)
                    )),
                    forceUseInitialTarget = self.deathTimer == config.PLAYER_DEATH_WAIT_TIME,
                    forceUseLastTarget = self.deathTimer < config.PLAYER_DEATH_WAIT_TIME
                )

            remainingEnemies.append(enemy)

        self.enemies = remainingEnemies

        if len(self.enemies) == 0:
            # The level was beaten
            if self.levelBeatenTimer is None:
                self.levelBeatenTimer = config.LEVEL_BEATEN_WAIT_TIME

        self.firstFrameOfLevel = False



def triple_compare(a, b, c):
    """Return a == c or b == c"""
    return a == c or b == c
