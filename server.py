import socket
import asyncio
import os
import sys
import threading
import time
import nn
import ga
import pickle
from const import *
from pygame.locals import *
import pygame
import subprocess
from player import *
import game
from multiprocessing.pool import ThreadPool
import time

def listenCommunication(clientSocket):
    global players
    try:
        playerReceived = clientSocket.recv(2048)

        if len(playerReceived) != 0 :
            try :
                p = pickle.loads(playerReceived)
                players.append(p)
            except :
                pass
        
        clientSocket.close()

    except Exception as inst:
        print("exp : " + str(inst))
        pass

def launchGame(name, score) :
     subprocess.call('python3 game.py mode=training filename=score\\' + str(name) + '.json speed=20 score=' + (str(score) if score > 2000 else '2000'))

def main(args) :
    global connections, s, players, bestPlayer, robotoFont, SCREEN, tAccept, gen, pendingThread
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Server')
    robotoFont = pygame.font.SysFont("Arial", 14)

    gen = 0 
    
    connections = []
    players = []
    bestPlayer = None
    pendingThread = 0

    print('launch')
    
    tTrain = threading.Thread(target=train)
    tTrain.start()
    while True:
        handleGameEvents()

        if(not tTrain.isAlive()):
            tTrain = threading.Thread(target=train)
            tTrain.start()

        # Background
        SCREEN.fill((0,0,0))

        # print(bestPlayer)
        if bestPlayer != None :
            showScore("BEST Input-Hidden", (10,0))
            showScore(bestPlayer.brain.weight_ih, (10, 25))
            showScore("BEST Hidden-Output", (10,50))
            showScore(bestPlayer.brain.weight_ho, (10, 75))
            showScore("Score", (10,100))
            showScore(bestPlayer.score, (10, 125))

        showScore(pendingThread, (10, SCREENHEIGHT - 50))
        showScore(gen, (10, SCREENHEIGHT - 25))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showScore(score, pos):
    label = robotoFont.render(str(score), 1, (255,255,255))
    SCREEN.blit(label, pos)

def handleGameEvents() :
    for event in pygame.event.get():
        # QUIT
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        
def save(brain, name) :
    json = brain.tojson()
    with open(name, 'w') as file :
        file.write(json)

def train() :
    global players, bestPlayer, gen, pendingThread
    threads = []
    print('Train')

    for i in range(0, len(players)) : 
        save(players[i].brain, "score\\" + str(i) + ".json")
    
    players.clear()
    
    p = ThreadPool(MAX_POPULATION)
    p.map(launchGame, range(MAX_POPULATION))
    
    maxScore = bestPlayer.score if bestPlayer != None else 0
    for player in players :
        if player.score > maxScore :
            maxScore = player.score
            bestPlayer = player

    if bestPlayer != None :
        save(bestPlayer.brain, "best.json")

    if len(players) > 0 :
        gen += 1
        players = ga.nextGeneration(players)

def launchGame(i):
    name = i
    score = bestPlayer.score if bestPlayer != None else 0
    p = game.main([
                'mode=training', 
                'filename=score\\' + str(name)+'.json',
                'speed=20', 
                'score=' + (str(score) if score > 2000 else '2000') 
            ])
    print(str(name) +  ' : '  + str(p.score))
    
if __name__ == '__main__':
    main(sys.argv)
