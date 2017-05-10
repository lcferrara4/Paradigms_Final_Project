import os
import sys
import math
import random
import zlib

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

import cPickle as pickle

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
	    # 1) Initialize game space
	    self.connected = False
	    pygame.init()
	    pygame.key.set_repeat(1,1000)
	    self.size = self.width, self.height = 940, 480
	    self.screen = pygame.display.set_mode(self.size)
	    pygame.display.set_caption("Air Hockey Game - Player 2")

	    # 2) Initialize all game objects
	    self.clock = pygame.time.Clock()
            self.background = pygame.image.load(BOARD_IMG)
	    self.background = self.scale_image(.5, self.background)
            self.player1 = Player1(self, MALLET1_IMG)
	    self.player2 = Player2(self, MALLET2_IMG)
	    self.puck = Puck(self)
	    self.scoreboard = ScoreBoard(self)
	    self.count = 0
	    self.winner = 0

	def game_loop(self):
            
		if self.connected:
			# 4) Tick speed regulation
			self.clock.tick(60)
			self.count+=1
				
			# 5) Reading user input
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					self.player2.move(event.key)

			# 6) Call tick on each game object
			self.player1.tick()
			self.player2.tick()
				
			# Send player 2 position to player 1 before ticking puck in case collision
			if self.count % 2 == 0: 
				self.write(zlib.compress(pickle.dumps([self.player2.rect.center])))
					
			self.puck.tick()
			self.scoreboard.tick()
				
			# Check for end of game
			if self.winner != 0:
				self.end_game()
			else:
				# 7) Update the screen
				self.screen.blit(self.background, (0,0))
				self.screen.blit(self.player1.image, self.player1.rect)
				self.screen.blit(self.player2.image, self.player2.rect)
				self.screen.blit(self.puck.image, self.puck.rect)
				self.screen.blit(self.scoreboard.label, self.scoreboard.rect)
				pygame.display.flip()

	def scale_image(self, scale, image):
		size = image.get_size()
		image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] *scale)))
		return image

	#function template to use other exit/write functions
	def quit(self):
		pass

	def write(self):
		pass

	def end_game(self):
		# Display game results
		self.screen.fill((0,0,0))
		winFont = pygame.font.SysFont("monospace", 42)
		if self.winner == 2:
			text = winFont.render("You win!!! Congrats!!", 1, (255, 255, 255))
		elif self.winner == 1:
			text = winFont.render("You lose!!! Womp....", 1, (255, 255, 255))
		text_rect = text.get_rect()
		text_rect.center = ([400, 200])
		self.screen.blit(text, text_rect)
		pygame.display.flip()

class ClientConn(Protocol):
	def __init__(self, gs):
	        self.gamespace_p2 = gs
		
	def connectionMade(self):
		self.gamespace_p2.connected = True
		self.transport.write("addplayer")
			
	def connectionLost(self, reason):
		reactor.stop()

	def dataReceived(self, data):
		# Unpack pickled data
		data = pickle.loads(zlib.decompress(data))
		if len(data) == 6:
			# if scores sent over as well
			self.gamespace_p2.player1.rect.center = data[0]
			self.gamespace_p2.puck.rect.center = data[1]
			self.gamespace_p2.scoreboard.score1 = pickle.loads(data[2])
			self.gamespace_p2.scoreboard.score2 = pickle.loads(data[3])
			self.gamespace_p2.puck.speedx = pickle.loads(data[4])
			self.gamespace_p2.puck.speedy = pickle.loads(data[5])
			self.gamespace_p2.player2.rect.centerx = self.gamespace_p2.width / 4 * 3
			self.gamespace_p2.player2.rect.centery = self.gamespace_p2.height / 2
		elif len(data) == 4:
			# if no scores sent
			self.gamespace_p2.player1.rect.center = data[0]
			self.gamespace_p2.puck.rect.center = data[1]
			self.gamespace_p2.puck.speedx = pickle.loads(data[2])
			self.gamespace_p2.puck.speedy = pickle.loads(data[3])

	def quit(self):
		self.transport.loseConnection()

	def write(self, data):
		self.transport.write(data)
	
class ClientConnFactory(ClientFactory):
    def __init__(self, gs):
        self.gs = gs
        self.client_connection = ClientConn(self.gs)

    def buildProtocol(self, addr):
        self.gs.quit = self.client_connection.quit
        self.gs.write = self.client_connection.write
        return self.client_connection

if __name__ == '__main__':
	gs = GameSpace()
	# 3) Start the game loop
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
        reactor.connectTCP(CLIENT_HOST, CLIENT_PORT, ClientConnFactory(gs))
	reactor.run()
	gs.game_loop()
	lc.stop()
