#!usr/bin/python

from threading import Thread, Semaphore
import sys
import random
import time

#global variables
rng = random.Random()
rng.seed(100)
inStash = 0
numGolfers = 0 
numinBucket = 0
balls_on_field = 0

class cartSwitch:
    def __init__(self):
        self.counter = 0
        self.mutex = Semaphore(1)
    def reset(self,semaphore2):
        self.mutex.acquire()
	#release all the threads which called cart
        while(self.counter > 0):
            semaphore2.release()
            self.counter -= 1 
        self.mutex.release()

    def unlock(self, semaphore):
	#release cart only on the first release ,by pass the rest
        self.mutex.acquire()
        if self.counter == 0:
            semaphore.release()
        self.counter += 1
        self.mutex.release()
#Light switch class
class GolfSwitch:
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
        if self.counter == 0:
            semaphore.release()
        self.mutex.release()
        
#semaphores

sendcart = Semaphore(0)
golferblock = Semaphore(0)
Lightswitch = cartSwitch()
fieldempty = Semaphore(1)
fieldlightswitch = GolfSwitch()
stashmutex = Semaphore(1)
ballonfield = Semaphore(1)
cartfree = Semaphore(1)
turnstile = Semaphore(1)
printmutex = Semaphore(1)
try:
    numGolfers = int(sys.argv[1])
    inStash = int(sys.argv[2])
    numinBucket = int(sys.argv[3])
except:
    print('Usage swing.py <numberofgolfer> <initial stash> <Bucket size>')
    exit()

def cart():
    global inStash
    global balls_on_field
    global ballonfield
    global sendcart
    global cartfree
    global Lightswitch
    global stashmutex
    global golferblock
    global fieldempty
    global turnstile
    global printmutex
    while True:
        sendcart.acquire() #wait for the first golfer to call for cart
        turnstile.acquire()
        fieldempty.acquire()
        printmutex.acquire()
        print('################################################################################')
        print('Stash = '+str(inStash)+'; Cart entering field')
        time.sleep(2)
        stashmutex.acquire() #mutex for  inStash global variable
	ballonfield.acquire() #mutex for balls_on_field variable 
        inStash += balls_on_field 
	ballonfield.release()
        stashmutex.release()
        print('Cart done, gathered '+str(balls_on_field)+' balls; Stash = '+str(inStash))
	ballonfield.acquire()
        balls_on_field = 0
	ballonfield.release()
        print('################################################################################')
        printmutex.release()
        Lightswitch.reset(golferblock) #release all blocked golfer thread who needs balls
        turnstile.release()
        fieldempty.release()
        time.sleep(1)

# golfer
def swing(id):
    bucket = 0
    global inStash
    global numGolfers
    global balls_on_field
    global sendcart
    global Lightswitch
    global cartfree
    global fieldlightswitch
    global turnstile
    global printmutex
    while True:
	printmutex.acquire()
        print('Golfer '+str(id)+' calling for bucket')
	printmutex.release()
        stashmutex.acquire()
        localstash = inStash
        stashmutex.release()
        if(localstash < numinBucket):
            Lightswitch.unlock(sendcart)  #Release cart to the field
            golferblock.acquire()	#block the golfers 
        stashmutex.acquire()
        inStash -= numinBucket
        printmutex.acquire()
        print('Golfer '+str(id)+' got '+ str(numinBucket) +' balls; Stash = ' +str(inStash))
        printmutex.release()
        stashmutex.release()
        
        for i in range(0,numinBucket):
            turnstile.acquire()
            turnstile.release()
            fieldlightswitch.lock(fieldempty)
            time.sleep(rng.random())
            ballonfield.acquire()
            balls_on_field += 1
            ballonfield.release()
            # simulate "swinging" here with random sleep
            printmutex.acquire()
            print('Golfer '+str(id)+'hit ball '+ str(i))
            printmutex.release()
            fieldlightswitch.unlock(fieldempty)
         #create threads = number of golfers
for i in range(numGolfers):
    t=Thread(target=swing,args=[i])
    t.start()
tcart = Thread(target = cart)
tcart.start()
    
