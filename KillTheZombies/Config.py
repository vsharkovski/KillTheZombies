import os


class Config:
    ### Do not change these
    STATUS_MENU = 0
    STATUS_PLAYING = 1
    STATUS_SHOP = 2
    STATUS_ENDED = 3
    
    CELL_NONE = 0
    CELL_EMPTY = 1
    CELL_WALL = 2
    CELL_DECO = 3

    PATH_DATA = os.path.join(os.getcwdu(), "data")
    PATH_STRUCTURES = os.path.join(PATH_DATA, "structures.json")
    PATH_SOUNDS = os.path.join(PATH_DATA, "sounds")

    PATH_IMAGES = os.path.join(PATH_DATA, "images")
    PATH_ENTITIES = os.path.join(PATH_IMAGES, "entities")
    PATH_DECORATIONS = os.path.join(PATH_IMAGES, "decorations")
    PATH_TEXT = os.path.join(PATH_IMAGES, "text")

    DEBUG = 0

    ### Graphics
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 660

    GRID_COLS = 36
    GRID_ROWS = 24

    INFOBAR_HEIGHT = 60 # Info bar will be from the top to here
    PADDING = 0

    GAME_X0 = PADDING # Left border of game area
    GAME_X1 = SCREEN_WIDTH - PADDING # Right border of game area
    GAME_Y0 = INFOBAR_HEIGHT # Top border of game area
    GAME_Y1 = SCREEN_HEIGHT - PADDING # Bottom border of game area

    CELL_WIDTH = (GAME_X1 - GAME_X0 + 1) // GRID_COLS
    CELL_HEIGHT = (GAME_Y1 - GAME_Y0 + 1) // GRID_ROWS

    ENTITY_MARGIN = 2
    BULLET_SIZE = 10

    ### Game variables
    # Timers    
    LEVEL_START_WAIT_TIME = 100
    LEVEL_BEATEN_WAIT_TIME = 130
    PLAYER_DEATH_WAIT_TIME = 200

    # Gameplay
    PLAYER_SPEED = 3
    BULLET_SPEED = 10

    PLAYER_HEALTH = 100

    # Number of frames before player can take damage again
    PLAYER_DAMAGE_COOLDOWN = 15

    # An enemy can spawn this many (or more) tiles away from the player
    ENEMY_MIN_SPAWN_DISTANCE = 20

    # Shop
    PLAYER_DAMAGE_VALUES = [20, 25, 30, 35, 40, 45, 50]
    PLAYER_DAMAGE_PRICES = [0, 200, 500, 1200, 2500, 5000, 10000]

    PLAYER_SHOT_COOLDOWN_VALUES = [20, 18, 15, 13, 10]
    PLAYER_SHOT_COOLDOWN_PRICES = [0, 500, 2000, 5000, 10000]

    PLAYER_PIERCING_VALUES = [1, 2, 3]
    PLAYER_PIERCING_PRICES = [0, 2500, 10000]

    # Level difficulty
    BASE_ENEMY_NUMBER = 2
    K_ENEMY_NUMBER = 1

    ### Enemies
    ENEMY_DATA = {
        "Ghost": {
            "spritePath": os.path.join(PATH_ENTITIES, "zombie4-32x.png"),
            "spriteFrames": 5,
            "speed": 1,
            "health": 100,
            "damage": 3,
            "reward": 40
        },
        "Runner": {
            "spritePath": os.path.join(PATH_ENTITIES, "zombie2-32x.png"),
            "spriteFrames": 5,
            "speed": 2,
            "health": 100,
            "damage": 3,
            "reward": 50
        },
        "Skipper": {
            "spritePath": os.path.join(PATH_ENTITIES, "zombie3-32x.png"),
            "spriteFrames": 5,
            "speed": 4,
            "health": 50,
            "damage": 3,
            "reward": 35
        }
    }

    ### Controls
    KEYS = {
        "CONTINUE": ENTER,
        "MOVE_UP": "w",
        "MOVE_DOWN": "s",
        "MOVE_LEFT": "a",
        "MOVE_RIGHT": "d",
        "SHOOT_UP": UP,
        "SHOOT_DOWN": DOWN,
        "SHOOT_LEFT": LEFT,
        "SHOOT_RIGHT": RIGHT,
        "SHOP_UPGRADE_DAMAGE": "1",
        "SHOP_UPGRADE_SHOT_COOLDOWN": "2",
        "SHOP_UPGRADE_PIERCING": "3"
    }

    ### Colors
    BULLET_COLORS = [
        ((252, 203, 68), (209, 168, 54)),
        ((255, 216, 110), (209, 178, 92))
    ]

    WALL_COLORS = [
        (30, 30, 30),
        (35, 35, 35),
        (40, 40, 40),
        (45, 45, 45),
        (50, 50, 50),
    ]

    WALL_COLORS2 = [
        (90, 90, 90),
        (80, 80, 80),
        (70, 70, 70),
        (60, 60, 60)
    ]

    FLOOR_COLORS = [
        (63, 99, 35),
        (77, 99, 35),
        (90, 99, 35),
        (99, 95, 35)
    ]

    FLOOR_COLORS2 = [
        (44, 97, 0),
        (58, 97, 0),
        (70, 97, 0),
        (84, 97, 0)
    ]

    FLOOR_COLORS3 = [
        (77, 97, 65),
        (88, 97, 65),
        (97, 96, 65),
        (94, 94, 69)
    ]

    ### Structures
    STRUCTURES = [
        [
            ".......",
            ".xxx.x.",
            ".....x.",
            ".x.....",
            ".x.xxx.",
            "......."
        ],
        [
            "xxx",
            "x..",
            "xxx"
        ],
        [
            "xxxxxxxx",
            "x......x",
            "........",
            "..xxxx..",
            "........",
            "x......x",
            "xxxxxxxx"
        ],
        [
            "xx..xx",
            "x....x",
            "......",
            "......",
            "x....x",
            "xx..xx"
        ],
        [
            "..x.x..",
            "..x.x..",
            "xxx.xxx",
            ".......",
            "xxx.xxx",
            "..x.x..",
            "..x.x.."
        ]
    ]

    STRUCTURE_SYMBOLS = {
        "0" : CELL_NONE,
        "." : CELL_EMPTY,
        "x" : CELL_WALL,
        "b" : CELL_DECO
    }



config = Config

print("Current working directory: {}\nData directory: {}".format(
    os.getcwdu(),
    config.PATH_DATA,
))
