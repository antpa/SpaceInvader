from nn import NeuralNetwork
from numpy import array
from const import *
from missile import Missile
import math

class Player:
    def __init__(self, brain = None):
        self.width = 20
        self.x = int(SCREENWIDTH /2 )
        self.y = int(BASEY - self.width - 5)
        self.missile = None

        self.velX    =  -8
        self.shooting = False

        self.score = 0
        self.fitness = 0
        self.bonus = MAXBONUS

        if(brain) :
            self.brain = brain.copy()
        else:
            self.brain = NeuralNetwork(9,10,3)

    def think(self, invaders, direction) :
        closestInvader = None
        closestDistance = SCREENWIDTH

        for invader in invaders :
            dist = math.hypot(self.x - invader.x, self.y - invader.y)
            if dist < closestDistance and dist > 0: 
                closestInvader = invader
                closestDistance = dist

        # the important thing in reinforcment : the inputs
        inputs = []
        inputs.append(float(self.x / SCREENWIDTH))
        inputs.append(float(self.y / SCREENHEIGHT))
        inputs.append(float(closestInvader.x / SCREENWIDTH) if closestInvader != None else 0)
        inputs.append(float(closestInvader.y / SCREENHEIGHT) if closestInvader != None else 0)
        inputs.append(1 if self.missile != None else 0)
        inputs.append(float(self.missile.x / SCREENWIDTH) if self.missile != None else 0)
        inputs.append(float(self.missile.y / SCREENHEIGHT) if self.missile != None else 0)
        inputs.append(float(self.bonus / MAXBONUS))
        inputs.append(float((direction + 1) / 2))

        h, output = self.brain.predict(array(inputs))
        if output[0][0] > 0.5:
            self.move(-1)
        elif output[1][0] > 0.5 :
            self.move(1)
        
        if output[2][0] > 0.5 :
            self.shoot()
    
    def addBonus(self) :
        self.score += self.bonus
        self.bonus = MAXBONUS

    def update(self) :
        self.score += 1
        self.bonus -= 1
        # if self.score % 1000 == 0 :
        #     print("score : " + str(self.score))
        if self.bonus < 0 :
            self.bonus = 0

        if self.missile == None :
            self.shooting = False

    def move(self, direction) :
        self.x += self.velX * direction
        self.x = min(self.x, SCREENWIDTH - self.width)
        self.x = max(self.x, 0)

    def shoot(self) :
        if not self.shooting :
            # print("fire")
            self.missile = Missile(self.x + self.width / 2, self.y, -1) # dir = -1 -> UP
            self.shooting = True
        # else : 
            # print("not fire")
            