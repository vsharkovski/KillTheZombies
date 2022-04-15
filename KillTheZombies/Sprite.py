from Config import config



class Sprite:
    def __init__(self, image, frameCount=1):
        """
        image: path to the image of the sprite
        frameCount: the number of frames in the sprite
        """
        self.image = image
        self.frameCount = frameCount
        self.frame = 0
        self.singleWidth = self.image.width // self.frameCount
        self.singleHeight = self.image.height


    def next_frame(self):
        self.frame = (self.frame + 1) % self.frameCount


    def set_frame(self, x):
        self.frame = x % self.frameCount


    def draw(self, p0, p1, frame=None):
        """
        Draw the sprite on the screen by cropping for the current frame.
        p0: Pair for the top-left corner to draw at
        p1: Pair for the bottom-right corner to draw at
        """
        if frame is None:
            frame = self.frame
    
        imageMode(CORNERS)
        image(
            self.image,
            p0.x, p0.y,
            p1.x, p1.y,
            self.singleWidth * frame, 0,
            self.singleWidth * (frame + 1) - 1, self.singleHeight
        )
