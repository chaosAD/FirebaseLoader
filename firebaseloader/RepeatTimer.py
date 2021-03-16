from threading import Timer
from threading import Event
import time

class RepeatTimer(Timer):
    def __init__(self, interval, function, args=[], kwargs={}):
        super().__init__(interval, function, *args, **kwargs)
        self.do_restart = False
        self.change_interval = False
        self.paused = Event()
        self.paused.set()
        
    def run(self):
        diff = 0
        while not self.finished.is_set() or self.change_interval:
            prev = time.time()
            # Note: The following will release the wait:       
            #       1) Timeout. This will not cause self.finished to set.
            #       2) Calling self.finished.set(). This will cause self.finished to set.
            while not self.finished.wait(self.interval - diff):
                self.function(*self.args, **self.kwargs)
                diff = 0
                prev = time.time()  
            if self.change_interval:                
                if not self.do_restart:
                    diff = time.time() - prev                 
                self.change_interval = False
                self.finished.clear()
            self.paused.wait() 

    def set_interval(self, new_interval, restart=False):
        self.interval = new_interval
        self.change_interval = True
        self.do_restart = restart
        self.finished.set()

    def restart(self):
        self.change_interval = True
        self.do_restart = True
        self.paused.set() 
        self.finished.set()
        
    def pause(self):
        self.paused.clear()
        self.finished.set()


if __name__ == "__main__":   
    def shout():
        print('hello!')
        
    t = RepeatTimer(5, shout)
    t.start()
    for i in range(30):    
        print(i)
        if i == 2:
            t.set_interval(6, restart=True)
        if i == 10:
            t.pause()
        if i == 15:
            t.restart()            
#            t.restart()
        time.sleep(1)    
    t.cancel()

        