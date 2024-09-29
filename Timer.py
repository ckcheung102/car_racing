import pygame

class Timer:

    def __init__(self, time,func=None, repeat=False):

        self.time=time
        self.func = func
        self.repeat=repeat

        self.start_time=0
        self.active= False

    def timer_on(self):

        self.active=True
        self.start_time=pygame.time.get_ticks()

    def time_out(self):

        self.active=False
        self.start_time=0
        if self.repeat:
            self.timer_on()

    def update(self):
        current_time=pygame.time.get_ticks()

        if current_time -self.start_time >= self.time :

            if self.func and self.start_time !=0:
                self.func()

            self.time_out()




