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
		# 1) Initialize game space
		self.connected = False
		pygame.init()
		pygame.key.set_repeat(1,1000)
		self.size = self.width, self.height = 940, 480
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("Air Hockey Game - Player 1")

		# 2) Initialize all game objects
		self.clock = pygame.time.Clock()
		self.background = pygame.image.load(BOARD_IMG)
		self.background = self.scale_image(.5, self.background)
		self.player1 = Player1(self, MALLET1_IMG)
		self.player2 = Player2(self, MALLET2_IMG)
		self.puck = Puck(self)
		self.scoreboard = ScoreBoard(self)

		self.winner = 0

		# Count for each time program loops for pickling
		self.count = 0
            
		# Check if puck is being hit from still at center
		self.FIRST = True

	def game_loop(self):

		# Start game once 2nd player connected
		if self.connected:
			# 4) Tick speed regulation
			self.clock.tick(60)

			self.count+=1

			# 5) Reading user input
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					self.player1.move(event.key)

			# 6) Call tick on each game object
			self.player1.tick()
			self.player2.tick()

			# Check for collisions between puck and players
			if self.collision(self.puck.rect.center, self.player1.rect.center):
				if self.FIRST:
					self.FIRST = False
				self.puck.change_speed(self.player1.rect)
			elif self.collision(self.puck.rect.center, self.player2.rect.center):
				if self.FIRST:
					self.FIRST = False
				self.puck.change_speed(self.player2.rect)

			self.puck.tick()
			self.scoreboard.tick()

			# Send position/speed data on every tick (not much data)
			# Important for player 2 to have correct positions
			# Only send scoreboard if needs updating -> someone scored
			if self.puck.scored != 0:
				self.write(zlib.compress(pickle.dumps([self.player1.rect.center, self.puck.rect.center, pickle.dumps(self.scoreboard.score1), pickle.dumps(self.scoreboard.score2), pickle.dumps(self.puck.speedx), pickle.dumps(self.puck.speedy)])))
			else:
				self.write(zlib.compress(pickle.dumps([self.player1.rect.center, self.puck.rect.center, pickle.dumps(self.puck.speedx), pickle.dumps(self.puck.speedy)])))

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

		else:
			# Keep displaying blank screen if no connection
			pygame.display.flip()

	def scale_image(self, scale, image):
		size = image.get_size()
		image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] *scale)))
		return image

	def collision(self,puck, player):
		distance = self.calc_collision(puck[0], puck[1], player[0], player[1])
		if self.FIRST and distance <=55:
			return True
		elif distance <=60:
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
	    if "addplayer" in data:
			self.gamespace_p1.connected = True
			# If receives "addplayer" and player 2 position at same time
			try:
				data = data.split("addplayer")[1]
				data = pickle.loads(zlib.decompress(data))
            	                self.gamespace_p1.player2.rect.center = data[0]
			except Exception as e:
				pass
	    else:
			# Load picked data
			data = pickle.loads(zlib.decompress(data))
			# Do not update player2 if someone scored
			# Needs to stay at start position
			if self.gamespace_p1.puck.scored == 0:
				self.gamespace_p1.player2.rect.center = data[0]
			else:
				self.gamespace_p1.puck.scored = 0

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
	# 3) Start the game loop
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnFactory(gs))
	reactor.run()
	lc.stop()
	gs.game_loop()
