import GUIManager as gui
from Config import config
from Pair import Pair


class Entity:
    """
    A rectangle with a sprite. Can move.
    """
    def __init__(self, p0, p1, sprite=None):
        """
        cell: position of the entity on the grid
        p0, p1: top left and bottom right corners on the screen
        sprite: the sprite for the entity
        """
        self.p0 = p0
        self.p1 = p1
        self.p0_prev = p0
        self.p1_prev = p1
        self.size = self.p1 - self.p0
        self.velocity = Pair(0, 0)
        self.sprite = sprite


    def draw(self):
        """Draw the entity on the screen."""
        if self.sprite is not None:
            self.sprite.draw(self.p0, self.p1)
            return
            
        rectMode(CORNERS)
        fill(255, 0, 0)
        noStroke()
        # stroke(0, 0, 0)
        # strokeWeight(4)
        rect(self.p0.x, self.p0.y, self.p1.x, self.p1.y)
    
    
    def get_corners(self):
        """
        Return the top left, top right,
        bottom left and bottom right corners, respectively.
        """
        return [
            self.p0,
            Pair(self.p1.x, self.p0.y), 
            Pair(self.p0.x, self.p1.y),
            self.p1
        ]


    def update(self, grid, considerWalls=True):
        """
        Update the position according to the velocity.
        Return (successX, successY), where
        successX: whether the entity could move in the
        X direction without intersecting with a wall
        successY: similar for Y direction
        """
        corners = self.get_corners()

        for moveX in [True, False]:
            for moveY in [True, False]:
                canMove = True
                velocity = Pair(
                    self.velocity.x if moveX else 0,
                    self.velocity.y if moveY else 0
                )

                for corner in corners:
                    newCorner = corner + velocity
                    cell = gui.screen_to_cell(newCorner)
                    if grid[cell.x][cell.y] == config.CELL_WALL:
                        canMove = False
                        break
                
                if canMove or not considerWalls:
                    self.p0_prev = Pair(self.p0.x, self.p0.y)
                    self.p1_prev = Pair(self.p1.x, self.p1.y)
                    self.p0 += velocity
                    self.p1 += velocity
                    return (moveX, moveY)

        return (False, False)


    def rollback_update(self, rollbackX, rollbackY):
        """
        Roll back the position to the one before calling update().
        rollbackX: whether to roll back the x position
        rollbackY: whether to roll back the y position
        """
        self.p0 = Pair(
            self.p0_prev.x if rollbackX else self.p0.x,
            self.p0_prev.y if rollbackY else self.p0.y
        )
        self.p1 = Pair(
            self.p1_prev.x if rollbackX else self.p1.x,
            self.p1_prev.y if rollbackY else self.p1.y
        )


    def is_colliding(self, other):
        """Determine whether the entity is colliding with the entity 'other'."""
        return (
            max(self.p0_prev.x, other.p0.x) <= min(self.p1_prev.x, other.p1.x),
            max(self.p0_prev.y, other.p0.y) <= min(self.p1_prev.y, other.p1.y),
            max(self.p0.x, other.p0.x) <= min(self.p1.x, other.p1.x),
            max(self.p0.y, other.p0.y) <= min(self.p1.y, other.p1.y)
        )


    def rollback_if_colliding(self, other):
        """
        Roll back the position if it just collided with other (entity).
        Return True if rolled back, False otherwise.
        """
        oldx, oldy, newx, newy = self.is_colliding(other)
        if newx and newy and ((newx and not oldx) or (newy and not oldy)):
            # collision happened, when it didn't happen before
            self.rollback_update(newx and not oldx, newy and not oldy)
            return True

        return False


    def teleport(self, target):
        """
        Teleport (set position) to the Pair target.
        Update p0 and p1 so the size of the entity is maintained.
        """
        self.p0 = Pair(target.x, target.y)
        self.p1 = self.p0 + self.size
        self.p0_prev = Pair(self.p0.x, self.p0.y)
        self.p1_prev = Pair(self.p1.x, self.p1.y)


    def __repr__(self):
        return "<Entity p0={} p1={} v={}>".format(self.p0, self.p1, self.velocity)
