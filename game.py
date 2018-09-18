from itertools import cycle
import random
import sys
from nn import *
import pygame
from pygame.locals import *
from player import Player
from invader import Invader
import ga
from const import *
import os.path
import socket
import pickle
import time

previous_score = 0
savedPlayers = []
players = []

def main(arg):
    global robotoFont, bestScoreEver, SCREEN, player, invaders, speed, previous_score, filename, trainningMode, trainningGen, s
    
    speed = 1
    scoreBeforeShowing = 0
    trainningMode = False
    filename = None
    for parameter in arg :
        if "score=" in parameter :
            scoreBeforeShowing = int(parameter[6:])
        if "speed=" in parameter :
            speed = int(parameter[6:])
        if "filename=" in parameter :
            filename = parameter[9:]
        if "mode=" in parameter :
            if parameter[5:] == "training" :
                trainningMode = True

    canDraw = False
    if scoreBeforeShowing == 0 and not trainningMode:
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption('Space Invader')
        robotoFont = pygame.font.SysFont("Roboto", 30)
        canDraw = True

    trainningGen = 0

    brain = None
    if filename != None and os.path.isfile(filename) :
        with open(filename, 'r') as file :
            brain = NeuralNetwork.fromjson(file.read())

    player = Player(brain)

    # Create invaders
    invaders = generateInvaders()

    bestScoreEver = 0
    hasCrashed = False
    while hasCrashed == False:
        if canDraw :
            handleGameEvents()

        if not canDraw and not trainningMode and bestScoreEver > scoreBeforeShowing :
            pygame.init()
            FPSCLOCK = pygame.time.Clock()
            SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
            pygame.display.set_caption('Space Invader')
            robotoFont = pygame.font.SysFont("Roboto", 30)
            canDraw = True

        for i in range(0, speed) :
            bestPlayerScore, bestScoreEver, hasCrashed = update()
        
        # draw
        if not canDraw :
            continue

        # Background
        SCREEN.fill((0,0,0))

        # Pipes
        for invader in invaders:
            pygame.draw.rect(SCREEN,(255,255,255), (invader.x, invader.y, invader.width, invader.height))

        # Ground
        pygame.draw.rect(SCREEN,(255,255,255), (BASEX, BASEY,SCREENWIDTH,SCREENHEIGHT - BASEY))

        # Player
        box_surface_circle = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(box_surface_circle, (255, 255, 255, 75), (int(player.width/2), int(player.width/2)),int(player.width/2), 0)
        SCREEN.blit(box_surface_circle, (player.x, player.y))

        # Missiles :
        if player.missile != None :
            pygame.draw.rect(SCREEN,(255,255,255), (player.missile.x, player.missile.y, MISSILEWIDTH, MISSILEHEIGHT))
       
        # Scores
        showScore(bestPlayerScore, (10,0))
        showScore(bestScoreEver, (10, 25))
        showScore(len(players), (SCREENWIDTH - 40, 0))
        showScore(trainningGen, (SCREENWIDTH - 40, 25))   
        pygame.display.update()
        FPSCLOCK.tick(FPS)
    
    return player

def handleGameEvents() :
    global speed
    for event in pygame.event.get():
        # QUIT
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        # SPEED UP
        if event.type == KEYDOWN and event.key == K_UP:
            speed += 1
            print(speed)
        # SPEED DOWN
        elif event.type == KEYDOWN and event.key == K_DOWN:
            speed -= 1
            print(speed)

        elif event.type == KEYDOWN and event.key == K_SPACE :
            player.shoot()
            print("shoot")

        if event.type == MOUSEBUTTONUP:
            # save(player)
            showBestNN(player)
            
        if speed < 1 :
            speed = 1   
        if speed > 100 : 
            speed = 100

def update():
    global previous_score, bestScoreEver, player, invaders, trainningGen, invLeft, invRight, invBot, direction, s, trainningMode

    # Change direction and invade
    if invLeft + INVVELX < 0 :
        direction *= -1 # to the right
        velY = INVVELY
    elif (invRight - INVVELX) > SCREENWIDTH :
        direction *= -1
        velY = INVVELY
    else :
        velY = 0
    
    invLeft = invLeft + (INVVELX * direction)
    invRight = invRight + (INVVELX * direction)
    invBot = invBot + velY
                
    # move invaders
    for invader in invaders:
        invader.x += INVVELX * direction
        invader.y += velY

    if player.missile != None :
        player.missile.update()
    
    destroyInvaders()

    # check crash
    crashTest = invBot >= player.y

    bestPlayerScore = 0
    player.think(invaders, direction)
    player.update()
    bestPlayerScore = max(player.score, bestPlayerScore)
    
    bestScoreEver = max(bestScoreEver, bestPlayerScore)
        
    if crashTest :
        if max(previous_score, bestScoreEver) > previous_score :
            # save(player)
            # showBestNN(player)
            previous_score = max(previous_score, bestScoreEver)

        if trainningMode :
            return bestPlayerScore, bestScoreEver, True
            # s.send(pickle.dumps(player))
            # time.sleep(2)
            # s.shutdown(2)
            # s.close()
            # sys.exit()
        else :
            # print("or Here")True
            player = Player(player.brain)

        # clear pipes
        invaders = generateInvaders()
        player.missile = None
        player.score = 0    
    
    if len(invaders) == 0 : 
        invaders = generateInvaders()
        player.addBonus()
        player.missile = None  

    return bestPlayerScore, bestScoreEver, False

def destroyInvaders() :
    global invaders, player, invBot, invLeft, invRight
    missile = player.missile
    if missile != None :
        if missile.x < invLeft or missile.x > invRight or missile.y > invBot :
            return
        
        collide = False
        invaderDestroyed = None
        for invader in invaders :
            invaderRect = pygame.Rect(invader.x, invader.y, invader.width, invader.height)
            missileRect = pygame.Rect(missile.x, missile.y, MISSILEWIDTH, MISSILEHEIGHT)

            collide = pixelCollision(missileRect, invaderRect)
            if collide :
                invaderDestroyed = invader
                player.score += 100
                # print("hit")
                continue
        
        if invaderDestroyed != None :
            player.missile = None
            invaders.remove(invaderDestroyed)
            calculateRectInvaders()
            # print("Destroy")
            return
    
        if missile.y < 0 :
            player.missile = None
            return

def calculateRectInvaders():
    global invLeft, invRight, invBot, invaders
    minX = SCREENWIDTH
    maxX = 0
    minBot = 0
    for invader in invaders :
        maxX = max(maxX, invader.x + invader.width)
        minX = min(minX, invader.x)
        minBot = max(minBot, invader.y + invader.height)

    invLeft = minX
    invRight = maxX
    invBot = minBot

def generateInvaders():
    global invLeft, invRight, invBot, direction
    # y of gap between upper and lower pipe
    invaders = []

    # init direction to go to the left
    direction = -1

    row = 4
    column = 7

    initialX = SCREENWIDTH / 2 - ((column * (INVWIDTH + INVGAP)) / 2)
    x = initialX
    y = 30

    invRight = x + (column * (INVWIDTH + INVGAP)) # 5 invaders per row
    invLeft = x
    invBot = y + (row * (INVHEIGHT + INVGAP)) # 3 rows

    for i in range(0, row) :
        for i in range(0, column):
            x = initialX + (INVWIDTH + INVGAP) * (i % column)
            invaders.append(Invader(x, y))
        y += INVHEIGHT + INVGAP
    
    return invaders

def save(player) :
    json = player.brain.tojson()
    with open(filename, 'w') as file :
        file.write(json)

def showBestNN(player):
    print("BEST Input-Hidden")
    print(player.brain.weight_ih)
    print("BEST Hidden-Output")
    print(player.brain.weight_ho)
    print("Score :")
    print(player.score)

def showScore(score, pos):
    label = robotoFont.render(str(score), 1, (255,255,255))
    SCREEN.blit(label, pos)

def checkCrash(player, invaders):
    # if player crashes into ground or sky
    if player.y + player.width >= BASEY - 1 or player.y <= 0:
        return True
    else:
        playerRect = pygame.Rect(player.x, player.y, player.width, player.width)

        for pipe in pipes:
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(pipe['x'], pipe['top'] - PIPEHEIGHT, PIPEWIDTH, PIPEHEIGHT)
            lPipeRect = pygame.Rect(pipe['x'], pipe['bottom'], PIPEWIDTH, PIPEHEIGHT)

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect)
            lCollide = pixelCollision(playerRect, lPipeRect)

            if uCollide or lCollide:
                return True

    return False

def pixelCollision(rect1, rect2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    return True

if __name__ == '__main__':
    main(sys.argv)
