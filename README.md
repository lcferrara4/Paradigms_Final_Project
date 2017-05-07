# Paradigms_Final_Project
 A multiplayer game that allows a minimum of two players to compete (or cooperate!) via a network connection using the PyGame and Twisted libraries. 

 Team Members: Lauren Ferrara and Emily Obadtch

 For this project, we decided to make a two player air hockey game. This game runs by a peer-to-peer network connection where player 1 starts first and waits for a connection from player 2 to begin game play. This project should be run using Python 2 for best results.

 Directions: 
1. The first player initializes a game on the command line by typing, "python player1.py".
2. A second player can then join this game in a different window by typing, "python player2.py" on the command line.
3. Each player can use the up, down, left, and right arrow keys to move their respective mallets. Player 1 is the red mallet on the left side of the air hockey table, and player 2 is the blue mallet on the right side of the table.
4. Players should try to make contact with the black puck in order to shoot it into the opposing player's goal.
5. If a goal is scored, the scoreboard will be updated to reflect this and the puck will be placed back in the middle of the table.
6. When either player reaches 7 goals, that player has won and the game ends. Players' screens will display a message reflecting their win/loss status.
7. At that time or anytime during game play, a player can click the X in the upper right corner of the screen to close the game.


The images used in this game were taken from the following links:

	* hockeyboard.png: https://www.cgtrader.com/3d-models/sports/equipment/air-hockey-game-ready

	* puck.png, mallet1.png, mallet2.png: http://imgur.com/gallery/KQgRv
