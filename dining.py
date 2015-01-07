#!/usr/bin/python

from threading import Thread, Semaphore
from time import sleep
from timeit import Timer
import sys
import random
import time

#global variables
rng = random.Random()
rng.seed(100)
numphil = 0
nummeals = 0
try:
    numphil = int(sys.argv[1])
    nummeals = int(sys.argv[2])
    print('Running dining philosophers simulation: '+str(numphil)+' philosophers,'\
    +str(nummeals)+' meals each')
except:
    print('Usage dining.py <numberofphil> <numofmeals>')
    exit()


def left(i): return i
def right(i): return (i+1)%numphil

forks = [Semaphore(1) for i in range(numphil)]
footman = Semaphore(numphil-1)
def lefty_get_fork(i):
    global forks
    forks[left(i)].acquire()
    forks[right(i)].acquire()
def righty_get_fork(i):
    global forks
    forks[right(i)].acquire()
    forks[left(i)].acquire()
    
def lefty_put_forks(i):
    global forks
    forks[right(i)].release()
    forks[left(i)].release()

def get_forks(i):
    global forks
    global footman
    footman.acquire()
    forks[right(i)].acquire()
    forks[left(i)].acquire()

def put_forks(i):
    global forks
    global footman
    forks[right(i)].release()
    forks[left(i)].release()
    footman.release()

state = ['thinking'] * numphil
sem = [Semaphore(0) for i in range(numphil)]
mutex = Semaphore(1)

def test(i):
    if state[i] == 'hungry' \
    and state[left(i)] != 'eating' \
    and state[right(i)] != 'eating':
        state[i] = 'eating'
    sem[i].release()

def T_get_forks(i):
    mutex.acquire()
    state[i] = 'hungry'
    test(i)
    mutex.release()
    sem[i].acquire()

def T_put_forks(i):
    mutex.acquire()
    state[i] = 'thinking'
    test(right(i))
    test(left(i))
    mutex.release()
    
def totime():
    #footman problem
    ts = []
    for i in range(numphil):
        ts.append(Thread(target=phil,args=[i]))
    for t in ts: t.start()
    for t in ts: t.join()
    
def toLefttime():
    #leftie rightie
    ts = []
    for i in range(numphil):
        ts.append(Thread(target=leftphil,args=[i]))
    for t in ts: t.start()
    for t in ts: t.join()

    
def toTanemTime():
    #leftie rightie
    ts = []
    for i in range(numphil):
        ts.append(Thread(target=Tanenbaumsphil,args=[i]))
    for t in ts: t.start()
    for t in ts: t.join()

def phil(id):
    mealcount = 0
    while True:
        time.sleep(rng.random())
        get_forks(id)
        mealcount+=1
        time.sleep(rng.random())
        put_forks(id)
        if mealcount == nummeals :
            break
            
def leftphil(id):
    mealcount = 0
    while True:
        #print('Philospher '+str(id)+' is thinking');
        time.sleep(rng.random())
        if(id == numphil-1):
            lefty_get_fork(id)
        else:
            righty_get_fork(id)
        #print('Philospher '+str(id)+' is eating');
        mealcount+=1
        #print 'meal count :'+ str(mealcount)
        time.sleep(rng.random())
        put_forks(id)
        if mealcount == nummeals :
            break
            

#Tanenbaums

def Tanenbaumsphil(id):
    mealcount = 0
    while True:
        time.sleep(rng.random())
        T_get_forks(id)
        mealcount+=1
        time.sleep(rng.random())
        T_put_forks(id)
        if mealcount == nummeals :
            break
        



if __name__ == '__main__':
    timer = Timer(totime)
    print("1. Footman solution, time elapsed: {:0.3f}s".format(timer.timeit(1)))
    
    timer = Timer(toLefttime)
    print("2. Left-handed solution, time elapsed: {:0.3f}s".format(timer.timeit(1)))
    
    timer = Timer(toTanemTime)
    print("3. Tanenbaum's  solution, time elapsed: {:0.3f}s".format(timer.timeit(1)))
    print 