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
        self.score1 = 0
        self.score2 = 0
        self.font = pygame.font.SysFont("monospace", 15)
        self.label = self.font.render("Player 1: {} vs Player 2: {}".format(self.score1, self.score2), 1, (255, 255, 0))
        self.rect = self.label.get_rect()
        self.rect.centerx = self.gs.width/3
        self.rect.centery = self.gs.height/10

    def tick(self):
        self.label = self.font.render("Player 1: {} vs Player 2: {}".format(self.score1, self.score2), 1, (255, 255, 0))
        winner = self.check_score()
        if winner == 1:
            self.gs.winner = winner
        elif winner == 2:
            self.gs.winner = winner
    
    def update_score(self, score1, score2):
        self.score1 = score1
        self.score2 = score2

    def check_score(self):
        if self.score1 >= 7:
            return 1
        elif self.score2 >= 7:
            return 2
        else:
            return 0

class Puck(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load(PUCK_IMG)
        self.image = self.gs.scale_image(.25, self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.gs.width/2
        self.rect.centery = self.gs.height/2

        self.speedx = 0
        self.speedy = 0
        self.scored = 0

    def tick(self):
        self.rect.centerx += self.speedx
        self.rect.centery += self.speedy
        
        #Minimal Friction on Surface
        if self.speedx > 0:
            self.speedx -=.08
        elif self.speedx < 0:
            self.speedx += .08
        
        if self.speedy > 0:
            self.speedy -=.08
        elif self.speedy < 0:
            self.speedy += .08

        #Check Goal
        #Player 1 Scored
        goal = self.check_goal()
        if goal ==1 or goal == 2:
            self.rect.centerx = self.gs.width/2
            self.rect.centery = self.gs.height/2
            self.speedx = 0
            self.speedy = 0
            self.gs.player1.rect.centerx = self.gs.width/4
            self.gs.player1.rect.centery = self.gs.height/2
            self.gs.player2.rect.centerx = self.gs.width/4 * 3
            self.gs.player2.rect.centery = self.gs.height/2
            self.gs.FIRST = True
            self.scored = 1

        if goal == 1:
            self.gs.scoreboard.score1+=1
        elif goal == 2:
            self.gs.scoreboard.score2+=1

        #Check Bounds
        if self.rect.centerx < 80:
            self.speedx = -self.speedx
            self.rect.centerx = self.rect.centerx + 10
        elif self.rect.centerx > 850:
            self.speedx = -self.speedx
            self.rect.centerx = self.rect.centerx - 10
        if self.rect.centery < 95:
            self.speedy = -self.speedy
            self.rect.centery = self.rect.centery + 10
        elif self.rect.centery > 400:
            self.speedy = -self.speedy
            self.rect.centery = self.rect.centery - 10

    def check_goal(self):
        if self.rect.centery > 200 and self.rect.centery < 295:
            if self.rect.centerx < 90:
                return 2
            elif self.rect.centerx > 850:
                return 1
        return 0

    def change_speed(self, rect):
        playerx = rect.centerx
        playery = rect.centery

        diff_y = (self.rect.centery - playery) / float(100)
        diff_x = (self.rect.centerx - playerx) / float(100)

        self.speedx = diff_x * 50
        self.speedy = diff_y * 50

class Player1(pygame.sprite.Sprite):
    def __init__(self, gs=None, image=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load(image)
        self.image = self.gs.scale_image(.15, self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.gs.width/4
        self.rect.centery = self.gs.height/2

        self.move_type = "NONE"

    def tick(self):
        mv = 30
        if self.move_type == "UP":
            self.rect = self.rect.move(0, -mv)
        if self.move_type == "DOWN":
            self.rect = self.rect.move(0, mv)
        if self.move_type == "LEFT":
            self.rect = self.rect.move(-mv, 0)
        if self.move_type == "RIGHT":
            self.rect = self.rect.move(mv, 0)


        #Check Bounds
        if self.rect.centerx >= (self.gs.width / 2) -5:
            self.rect.centerx = (self.gs.width/2) -10
        elif self.rect.centerx < 90:
            self.rect.centerx = 95
        if self.rect.centery < 90:
            self.rect.centery = 95
        elif self.rect.centery > 390:
            self.rect.centery = 385

        self.move_type = "NONE"

    def move(self, key):
        if key == pygame.K_UP:
            self.move_type = "UP"
        if key == pygame.K_DOWN:
            self.move_type = "DOWN"
        if key == pygame.K_LEFT:
            self.move_type = "LEFT"
        if key == pygame.K_RIGHT:
            self.move_type = "RIGHT"

class Player2(pygame.sprite.Sprite):
    def __init__(self, gs=None, image=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load(image)
        self.image = self.gs.scale_image(.15, self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.gs.width/4 * 3
        self.rect.centery = self.gs.height/2 

        self.move_type = "NONE"

    def tick(self):
        mv = 30
        if self.move_type == "UP":
            self.rect = self.rect.move(0, -mv)
        if self.move_type == "DOWN":
            self.rect = self.rect.move(0, mv)
        if self.move_type == "LEFT":
            self.rect = self.rect.move(-mv, 0)
        if self.move_type == "RIGHT":
            self.rect = self.rect.move(mv, 0)
        

        #Check Bounds
        if self.rect.centerx <= (self.gs.width / 2) +5:
            self.rect.centerx = (self.gs.width/2) + 10
        elif self.rect.centerx > 850:
            self.rect.centerx = 845
        if self.rect.centery < 90:
            self.rect.centery = 95
        elif self.rect.centery > 390:
            self.rect.centery = 385

        self.move_type = "NONE"

    def move(self, key):
        if key == pygame.K_UP:
            self.move_type = "UP"
        if key == pygame.K_DOWN:
            self.move_type = "DOWN"
        if key == pygame.K_LEFT:
            self.move_type = "LEFT"
        if key == pygame.K_RIGHT:
            self.move_type = "RIGHT"


