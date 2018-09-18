from const import *

class Missile :
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

        self.vel = 6

    def update(self) :
        self.y += self.direction * self.vel