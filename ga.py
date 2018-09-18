from player import Player
import const
import random

def nextGeneration(parents):
    calculateFitness(parents)
    childs = []
    for i in range(0, const.MAX_POPULATION) :
        childs.append(pickOne(parents))
    
    return childs

def pickOne(parents):
    index = 0
    r = random.random()
    while(r > 0) :
        r = r - parents[index].fitness
        index += 1

    index -= 1
    player = parents[index]
    child = Player(player.brain)
    child.brain.mutate(0.1)
    return child

def calculateFitness(parents):
    sum = 0
    for player in parents :
        sum += player.score

    for player in parents :
        player.fitness = player.score / sum
        