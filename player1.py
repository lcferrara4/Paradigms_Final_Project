import os
import sys
import math
import random
import zlib

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

import cPickle as pickle

import pygame
from pygame.locals import *

from GameObjects import *

SERVER_PORT = 40089
PUCK_IMG = './puck.png'
MALLET1_IMG = './mallet1.png'
MALLET2_IMG = './mallet2.png'
BOARD_IMG = './hockeyboard.png'

class GameSpace():
        def __init__(self):
            self.connected = False
            pygame.init()
            pygame.key.set_repeat(1,1000)
            self.size = self.width, self.height = 940, 480
            self.screen = pygame.display.set_mode(self.size)
            pygame.display.set_caption("Air Hockey Game - Player 1")

            # Set up game objects
            self.clock = pygame.time.Clock()
            self.background = pygame.image.load(BOARD_IMG)
            self.background = self.scale_image(.5, self.background)
            self.player1 = Player1(self, MALLET1_IMG)
            self.player2 = Player2(self, MALLET2_IMG)
            self.puck = Puck(self)
            self.scoreboard = ScoreBoard(self)

            self.winner = 0

            #count for each time program loops for pickling
            self.count = 0
            
            #Check if puck is being hit from still at center
            self.FIRST = True

        def game_loop(self):

            if self.connected:
                self.clock.tick(60)
                
                self.count+=1
                if self.collision(self.puck.rect.center, self.player1.rect.center):
                    if self.FIRST:
                        self.FIRST = False
                    self.puck.change_speed(self.player1.rect)
                elif self.collision(self.puck.rect.center, self.player2.rect.center):
                    if self.FIRST:
                        self.FIRST = False
                    self.puck.change_speed(self.player2.rect)


                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                    elif event.type == pygame.KEYDOWN:
                        self.player1.move(event.key)

                self.player1.tick()
                self.player2.tick()
                self.puck.tick()
                self.scoreboard.tick()

                #send coordinates every other tick
                if self.count % 4 == 0:
                    self.write(zlib.compress(pickle.dumps([self.player1.rect.center, self.puck.rect.center, pickle.dumps(self.scoreboard.score1), pickle.dumps(self.scoreboard.score2), pickle.dumps(self.puck.speedx), pickle.dumps(self.puck.speedy)])))
                elif self.count % 2 == 0:
                    self.write(zlib.compress(pickle.dumps([self.player1.rect.center])))

                if self.winner != 0:
                    self.end_game()
                else:
                    self.screen.blit(self.background, (0,0))
                    self.screen.blit(self.player1.image, self.player1.rect)
                    self.screen.blit(self.player2.image, self.player2.rect)
                    self.screen.blit(self.puck.image, self.puck.rect)
                    self.screen.blit(self.scoreboard.label, self.scoreboard.rect)

                    pygame.display.flip()

            else:
                pygame.display.flip()

        def scale_image(self, scale, image):
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] *scale)))
            return image

        def collision(self,puck, player):
            distance = self.calc_collision(puck[0], puck[1], player[0], player[1])
            if self.FIRST and distance <=55:
                return True
            elif distance <=65:
                return True
            else:
                return False

        def calc_collision(self,x1, y1, x2, y2):
            return (math.sqrt(pow((x2-x1),2)+pow((y2-y1),2)))

        def quit(self):
            pass

        def write(self, data):
            pass

        def end_game(self):
            self.screen.fill((0,0,0))
            winFont = pygame.font.SysFont("monospace", 42)
            if self.winner == 1:
                text = winFont.render("You win!!! Congrats!!", 1, (255, 255, 255))
            elif self.winner == 2:
                text = winFont.render("You lose!!! Womp....", 1, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = ([400, 200])
            self.screen.blit(text, text_rect)
            pygame.display.flip() 

class ServerConn(Protocol):
	def __init__(self, addr, gs):
            self.addr = addr
	    self.gamespace_p1 = gs
        
        def connectionMade(self):
            pass

	def dataReceived(self, data):
	    if data == "addplayer":
		self.gamespace_p1.connected = True
            #pickled data
            else:
                data = pickle.loads(zlib.decompress(data))
                self.gamespace_p1.player2.rect.center = data[0]

        def connectionLost(self, reason):
            reactor.stop()

        def quit(self):
            self.transport.loseConnection()

        def write(self, data):
            self.transport.write(data)

class ServerConnFactory(Factory):
	def __init__(self, gs):
	    self.gs = gs

	def buildProtocol(self, addr):
            self.server_connection = ServerConn(addr, self.gs)
            self.gs.quit = self.server_connection.quit # loses connection
            self.gs.write = self.server_connection.write
	    return self.server_connection

if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
	lc.stop()
        gs.game_loop()
