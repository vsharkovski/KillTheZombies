import os
import random

from Config import config
from Pair import Pair


def screen_to_cell(pos):
    """
    Return the cell in the grid to which
    the screen pixel (pos.x, pos.y) corresponds to.
    """
    return Pair(
        (pos.x - config.GAME_X0) // config.CELL_WIDTH,
        (pos.y - config.GAME_Y0) // config.CELL_HEIGHT,
    )


def cell_to_screen(cell):
    """
    Return the screen pixel to which the
    top left corner of the grid cell corresponds to.
    """
    return Pair(
        cell.x * config.CELL_WIDTH + config.GAME_X0,
        cell.y * config.CELL_HEIGHT + config.GAME_Y0
    )


def draw_title(maxLevelReached=0):
    """Draw the title screen."""
    background(0, 0, 0)
    
    imageMode(CORNERS)
    image(loadImage(os.path.join(config.PATH_TEXT, "Logo.gif")), 130, 70, 780, 270)
    
    fill(30, 121, 0)
    textSize(20)
    textAlign(CENTER)
    plurality = "levels" if maxLevelReached != 1 else "level"
    text("Best score: {} {}.".format(maxLevelReached, plurality),
        0, 320,config.SCREEN_WIDTH, 360)
    text("Controls: Use WASD to move and the arrow keys to shoot!",
        0, 380, config.SCREEN_WIDTH, 420)
    
    image(loadImage(os.path.join(config.PATH_TEXT, "Start Message.gif")), 240, 480, 660, 580)


def draw_game_over(level):
    """Draw the game over screen."""
    background(0, 0, 0)
    
    imageMode(CORNERS)
    image(loadImage(os.path.join(config.PATH_TEXT, "Game Over.gif")), 200, 70, 680, 270)
    
    fill(30, 121, 0)
    textSize(20)
    textAlign(CENTER)
    plurality = "levels" if level != 1 else "level"
    text("You survived {} {}.".format(level, plurality),
        0, 355, config.SCREEN_WIDTH, 400)
    
    image(loadImage(os.path.join(config.PATH_TEXT, "End Message.gif")), 140, 480, 770, 580)


def draw_shop(money, damageLevel, shotCooldownLevel, piercingLevel):
    """Draw the shop screen."""
    background(0, 0, 0)
    
    imageMode(CORNERS)
    image(loadImage(os.path.join(config.PATH_TEXT, "Shop.gif")), 340, 0, 560, 200)
    
    fill(30, 121, 0)
    textSize(15)
    textAlign(BASELINE)
    text("Your money: ${}".format(money), 100, 210)
    
    # Shop section for damage
    dmgString = None
    if damageLevel + 1 >= len(config.PLAYER_DAMAGE_PRICES):
        dmgString = "Damage: Max level! ({} damage)".format(
            config.PLAYER_DAMAGE_VALUES[damageLevel]
        )
    else:
        dmgString = "Damage: Level {} - Press {} to upgrade for ${}".format(
            damageLevel,
            config.KEYS["SHOP_UPGRADE_DAMAGE"],
            config.PLAYER_DAMAGE_PRICES[damageLevel+1]
        )

    text(dmgString, 100, 260)
    draw_shop_circles(150, 300, damageLevel-1, len(config.PLAYER_DAMAGE_PRICES)-1)

    # Shop section for fire rate
    shotCdString = None

    if shotCooldownLevel + 1 >= len(config.PLAYER_SHOT_COOLDOWN_PRICES):
        shotCdString = "Fire rate: Max level!"
    else:
        shotCdString = "Fire rate: Level {} - Press {} to upgrade for ${}".format(
            shotCooldownLevel,
            config.KEYS["SHOP_UPGRADE_SHOT_COOLDOWN"],
            config.PLAYER_SHOT_COOLDOWN_PRICES[shotCooldownLevel+1]
        )
    
    text(shotCdString, 100, 360)
    draw_shop_circles(150, 400, shotCooldownLevel-1, len(config.PLAYER_SHOT_COOLDOWN_PRICES)-1)
    
    # Shot section for piercing
    piercingString = None

    if piercingLevel + 1 >= len(config.PLAYER_PIERCING_PRICES):
        piercingString = "Piercing: Max level! ({} enemies)".format(
            config.PLAYER_PIERCING_VALUES[piercingLevel]
        )
    else:
        piercingString = "Piercing: Level {} ({} enemies) - Press {} to upgrade for ${}".format(
            piercingLevel,
            config.PLAYER_PIERCING_VALUES[piercingLevel],
            config.KEYS["SHOP_UPGRADE_PIERCING"],
            config.PLAYER_PIERCING_PRICES[piercingLevel+1]
        )

    text(piercingString, 100, 460)
    draw_shop_circles(150, 500, piercingLevel-1, len(config.PLAYER_PIERCING_PRICES)-1)
    
    image(loadImage(os.path.join(config.PATH_TEXT, "Shop Message.gif")), 140, 550, 770, 650)


def draw_info(health, maxHealth, money, level):
    """Draw the info bar at the top of the screen."""
    rectMode(CORNERS)
    noStroke()
    fill(*config.WALL_COLORS[0])
    rect(0, 0, config.SCREEN_WIDTH, config.INFOBAR_HEIGHT)

    textAlign(CENTER, CENTER)
    textSize(20)
    noStroke()
    fill(30, 121, 0)
    text(
        "Health: {}/{}".format(health, maxHealth),
        0, 0,
        config.SCREEN_WIDTH//3, config.INFOBAR_HEIGHT
    )
    text(
        "Level: {}".format(level),
        config.SCREEN_WIDTH//3, 0,
        (config.SCREEN_WIDTH//3)*2, config.INFOBAR_HEIGHT
    )
    text(
        "Money: ${}".format(money),
        (config.SCREEN_WIDTH//3)*2, 0,
        config.SCREEN_WIDTH, config.INFOBAR_HEIGHT
    )

    if config.DEBUG:
        textSize(12)
        textAlign(LEFT, TOP)
        color = get(mouseX, mouseY)
        text(
            "Mouse at ({}, {}), color ({}, {}, {})".format(
                mouseX,
                mouseY,
                int(red(color)), int(green(color)), int(blue(color))
            ),
            0,
            0
        )


def draw_game_area(map, player, enemies, bullets, forceDrawMap):
    """Draw the game area, showing the grid and entities.""" 
    # draw floor and walls
    rectMode(CORNERS)
    strokeWeight(1)
    for x in range(config.GRID_COLS):
        for y in range(config.GRID_ROWS):
            # if not forceDrawMap and map.eData[x][y] <= 0:
            #     continue
            if map.colorGrid[x][y] is None:
                continue

            stroke(*map.colorGrid[x][y])
            fill(*map.colorGrid[x][y])
            p0 = cell_to_screen(Pair(x, y))
            p1 = cell_to_screen(Pair(x+1, y+1)) - Pair(1, 1)
            rect(p0.x, p0.y, p1.x, p1.y)
    
    if config.DEBUG:
        for x in range(config.GRID_COLS):
            for y in range(config.GRID_ROWS):
                p0 = cell_to_screen(Pair(x, y))
                p1 = cell_to_screen(Pair(x+1, y+1)) - Pair(1, 1)
                if map.grid[x][y] == config.CELL_WALL:
                    fill(255, 255, 255)
                    textAlign(CENTER, CENTER)
                    textSize(12)
                    if x == 0 and y != 0:
                        text(str(y), p0.x, p0.y, p1.x, p1.y)
                    elif y == 0 and x != 0:
                        text(str(x), p0.x, p0.y, p1.x, p1.y)
                else:
                    continue
                    stroke(200, 200, 200)
                    strokeWeight(1)
                    # heat map
                    if map.bfsDistance[x][y] is None:
                        noFill()
                    else:
                        fill(min(255, 10*map.bfsDistance[x][y]), 255, 255)
                    rect(p0.x, p0.y, p1.x, p1.y)
                    if map.bfsDistance[x][y] is not None:
                        # number
                        fill(180, 180, 180)
                        textAlign(CENTER, CENTER)
                        text(str(map.bfsDistance[x][y]), p0.x, p0.y, p1.x, p1.y)

    # draw decorations
    for x in range(config.GRID_COLS):
        for y in range(config.GRID_ROWS):
            # if not forceDrawMap and map.eData[x][y] <= 0:
            #     continue
            if map.grid[x][y] == config.CELL_DECO:
                sprite = map.decorationGrid[x][y]
                p0 = cell_to_screen(Pair(x, y))
                p1 = cell_to_screen(Pair(x+1, y+1)) - Pair(1, 1)
                sprite.draw(p0, p1)

    # draw entities
    if player.alive:
        player.draw()

    for e in enemies:
        e.draw()

    for b in bullets:
        b.draw()


def draw_shop_circles(topX, topY, filledCount, totalCount):
    ellipseMode(CORNER)
    for i in range(totalCount):
        if i <= filledCount:
            fill(30, 121, 0)
            stroke(30, 121, 0)
            ellipseMode(RADIUS)
            ellipse(topX + (i*45), topY, 15, 15)
        else:
            noFill()
            stroke(30, 121, 0)
            ellipseMode(RADIUS)
            ellipse(topX + (i*45), topY, 15, 15)
