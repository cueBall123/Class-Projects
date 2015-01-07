#!usr/bin/python

from threading import Thread, Semaphore
from collections import deque
import sys
import random
import time
import itertools


#global variables
rng = random.Random()
rng.seed(100)

numLeaders = 0
numFollowers = 0
leaderq = deque()
followerq = deque()

#sempahore
followerwait = Semaphore(0)
leaderwait = Semaphore(0)
floormutex = Semaphore(1)
printmutex = Semaphore(1)
turnstile  = Semaphore(1)
followerenter = Semaphore(0)
class LightSwitch:
    def __init__(self):
        self.counter = 0
        self.mutex = Semaphore(1)
    
    def lock(self, semaphore):
        self.mutex.acquire()
        self.counter += 1
        if self.counter == 1:
            semaphore.acquire()
        self.mutex.release()

    def unlock(self, semaphore):
        self.mutex.acquire()
        self.counter -= 1
        #print str(self.counter)
        if self.counter == 0:
            semaphore.release()
        self.mutex.release()

FloorLightSwitch = LightSwitch()

def start_music(music):
    global printmutex
    printmutex.acquire()
    print'** Band leader started playing '+music+' **'
    printmutex.release()
def end_music(music):
    printmutex.acquire()
    print'** Band leader stopped playing '+music+' **'
    printmutex.release()
def band_leader():
    global floormutex
    global turnstile
    for music in itertools.cycle(['waltz','tango','foxtrot']):
        start_music(music)
        time.sleep(1)
        turnstile.acquire()
        floormutex.acquire()
        end_music(music)
        turnstile.release()
        floormutex.release()
def enter_floor(type,number):
    global floormutex
    global followerenter
    time.sleep(rng.random())
    if(type == 'L'):
        printmutex.acquire()
        print 'Leader '+str(number)+' entered floor'
        printmutex.release()

    if(type == 'F'):
        printmutex.acquire()
        print 'Follower '+str(number)+' entered floor'
        printmutex.release()
        followerenter[number].release()

def dance(type,number):
    global followerenter
    if(type == 'L'):
        #deque.appendleft(id)
        temp = followerq.pop()
        followerenter[temp].acquire()
        printmutex.acquire()
        print 'Leader '+str(number)+ ' and Follower '+str(temp)+ ' are dancing. '
        printmutex.release()
        time.sleep(rng.random())
        
    if(type =='F'):
        time.sleep(rng.random())
        
def line_up(type,number):
    if(type == 'L'):
        printmutex.acquire()
        print 'Leader '+str(number)+' getting back in line.'
        printmutex.release()
    if(type == 'F'):
        printmutex.acquire()
        print 'Follower '+str(number)+' getting back in line.'
        printmutex.release()
try:
    numLeaders = int(sys.argv[1])
    numFollowers = int(sys.argv[2])
    global followerenter
    followerenter = [Semaphore(0) for i in range(numFollowers)]
except:
    print('Usage dancers <numberofleaders> <numberoffollowers>')
    exit()


def leader(id):
    global FloorLightSwitch
    global floormutex
    global followerwait
    global leaderwait
    while True:
        leaderwait.release()
        followerwait.acquire()
        turnstile.acquire()
        turnstile.release()
        FloorLightSwitch.lock(floormutex)
        enter_floor('L',id)
        dance('L',id)
        line_up('L',id)
        FloorLightSwitch.unlock(floormutex)    
def follower(id):
    global FloorLightSwitch
    global floormutex
    global followerwait
    global leaderwait
    while True:
        followerq.appendleft(id)
        followerwait.release()
        leaderwait.acquire()
        turnstile.acquire()
        turnstile.release()
        FloorLightSwitch.lock(floormutex)
        enter_floor('F',id)
        dance('F',id)
        line_up('F',id)
        FloorLightSwitch.unlock(floormutex)

tbandleader = Thread(target=band_leader)
tbandleader.start()
for i in range(0,numLeaders):
    tleader = Thread(target=leader,args=[i])
    tleader.start()
for j in range(0,numFollowers):
    tfollower = Thread(target=follower,args=[j])
    tfollower.start()