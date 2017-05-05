import os
import sys
import math
import random

import pygame
from pygame.locals import *

SERVER_PORT = 40089
PUCK_IMG = './puck.png'
MALLET1_IMG = './mallet1.png'
MALLET2_IMG = './mallet2.png'
BOARD_IMG = './hockeyboard.png'

class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.font = pygame.font.SysFont("monospace", 15)
        self.label = self.font.render("Hello", 1, (255, 255, 0))
        self.rect = self.label.get_rect()
        self.rect.centerx = self.gs.width/3
        self.rect.centery = self.gs.height/10

    def tick(self):
        self.update_score()

    def update_score(self):
        pass

class Puck(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load(PUCK_IMG)
        self.image = self.gs.scale_image(.25, self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.gs.width/2
        self.rect.centery = self.gs.height/2

    def tick(self):
        self.move()

    def move(self):
        pass



class Player(pygame.sprite.Sprite):
    def __init__(self, gs=None, image=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load(image)
        self.image = self.gs.scale_image(.25, self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.gs.width/4
        self.rect.centery = self.gs.height/2

    def tick(self):
        self.move()

    def move(self):
        key = pygame.key.get_pressed()
        mv = 10
        
        if key[pygame.K_UP]:
            self.rect = self.rect.move(0, -mv)
        if key[pygame.K_DOWN]:
            self.rect = self.rect.move(0, mv)
        if key[pygame.K_LEFT]:
            self.rect = self.rect.move(-mv, 0)
        if key[pygame.K_RIGHT]:
            self.rect = self.rect.move(mv, 0)


