class Pair:
    """Vector2 class."""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    

    def __add__(self, other):
        return Pair(self.x + other.x, self.y + other.y)
    

    def __sub__(self, other):
        return Pair(self.x - other.x, self.y - other.y)
    

    def __mul__(self, other):
        return Pair(self.x * other.x, self.y * other.y)


    def __div__(self, other):
        return Pair(self.x / other.x, self.y / other.x)


    def __repr__(self):
        return "({}, {})".format(self.x, self.y)


    def midpoint(self, other):
        return Pair((self.x + other.x)//2, (self.y + other.y)//2)
