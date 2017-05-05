import os
import sys
import math
import random

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

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
            self.connected = 0
            pygame.init()
            pygame.key.set_repeat
            self.size = self.width, self.height = 940, 480
            self.screen = pygame.display.set_mode(self.size)
            pygame.display.set_caption("Air Hockey Game - Player 1")

            # Set up game objects
            print('set up')
            self.clock = pygame.time.Clock()
            self.background = pygame.image.load(BOARD_IMG)
            self.background = self.scale_image(.5, self.background)
            self.player1 = Player(self, MALLET1_IMG)
            self.player2 = Player(self, MALLET2_IMG)
            self.puck = Puck(self)
            self.scoreboard = ScoreBoard(self)
                
        def main(self):

            if self.connected:
                print('connected in gamespace main')
                
                self.clock.tick(60)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        self.player1.move()
                        
                print('ticking')
                self.player1.tick()
                self.player2.tick()
                self.puck.tick()
                self.scoreboard.tick()

                print('blitting')
                self.screen.blit(self.background, (0,0))
                self.screen.blit(self.player1, self.player1.rect)
                self.screen.blit(self.player2, self.player2.rect)
                self.screen.blit(self.puck, self.puck.rect)
                self.screen.blit(self.scoreboard.label, self.scoreboard.rect)

                print('flipping')
                pygame.display.flip()

            else:
                pygame.display.flip()

        def scale_image(self, scale, image):
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] *scale)))
            return image

class ServerConn(Protocol):
	def __init__(self, addr, gs):
            self.addr = addr
	    self.gamespace_p1 = gs

	def dataReceived(self, data):
            print('data received')
	    if data == "addplayer":
		self.gamespace_p1.connected = 1

        def connectionLost(self, reason):
            print('connection lost')
            reactor.stop()



class ServerConnFactory(Factory):
	def __init__(self, gs):
	    self.server_connection = None
	
	def buildProtocol(self, addr):
            self.server_connection = ServerConn(addr, gs)
	    return self.server_connection

if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.main)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
	lc.stop()
