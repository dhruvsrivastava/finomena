# finomena

Requirements:
Flask
Redis
Python

Instructions:
Clone git repository

1. cd finomena [Enter Directory]

2. python app.py [Start the Flask Server]

3. redis-server [Start redis server]

4. Navigate to localhost:5000 to access home page

5. Server is running on port 0.0.0.0 that means users can access this website on a.b.c.d:5000 where a.b.c.d is the ip of the server


API:

1. /login
Asks the user for a unique username and assigns it. List of usernames is maintained using db.

2. /game/create/
Automatically creates a new game for the user and returns the unique "gameID" to access the game

3. /specify/gameID
Allows user to specify the dimensions of the board of the game with ID : "gameID".

4. /play/gameID
Allows user to enter an existing game with unique ID : "gameID". If such a game does not exist , user is asked to create such a game. 

