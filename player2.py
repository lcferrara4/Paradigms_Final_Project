import os
import sys
import math
import random

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import pygame
from pygame.locals import *

from GameObjects import *

CLIENT_HOST = 'ash.campus.nd.edu'
CLIENT_PORT = 40089
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
	    pygame.display.set_caption("Air Hockey Game - Player 2")

	    #2. set up game objects
            print('set up')
	    self.clock = pygame.time.Clock()
            self.background = pygame.image.load(BOARD_IMG)
            self.background = self.scale_image(.5, self.background)
            self.player1 = Player(self, MALLET1_IMG)
            self.player2 = Player(self, MALLET2_IMG)
            self.puck = Puck(self)
            self.scoreboard = ScoreBoard(self)

        def main(self):
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.player2.move()

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

        def scale_image(self, scale, image):
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] *scale)))
            return image


class ClientConn(Protocol):
	def __init__(self, gs):
	    self.gamespace_p2 = gs
		
	def connectionMade(self):
	    print('connection made')
            self.gamespace_p2.connected = 1
            self.transport.write("addplayer")
	

class ClientConnFactory(ClientFactory):
	def __init__(self, gs):
	    self.client_connection = ClientConn(gs)
	
	def buildProtocol(self, addr):
	    return self.client_connection

if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.main)
	lc.start(1/60)
	reactor.connectTCP(CLIENT_HOST, CLIENT_PORT, ClientConnFactory(gs))
	reactor.run()
	lc.stop()
