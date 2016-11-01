from flask import Flask
from flask import render_template , redirect , url_for
from flask import request , g
from flask import session , escape
from functools import wraps
import redis

app = Flask(__name__)
app.redis = redis.StrictRedis(host = 'localhost' , port = 6379 , db = 0)
app.secret_key = 'secret_session_key'

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try :
			if session['user'] is None:
				return redirect(url_for('login'))
			return f(*args , **kwargs)
		except KeyError:
			return redirect(url_for('login'))
	return decorated_function

@app.route('/')
@login_required
def index():
	return render_template('index.html' , username = session['user'])

@app.route('/login' , methods = ['GET' , 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		if app.redis.get(username) == "1":
			err = "Username Already Exists"
			return render_template('login.html' , error = err)
		app.redis.set(username , "1")
		session['user'] = username
		return redirect(url_for('index'))
	if 'user' in session:	#user has already logged in
		return redirect(url_for('index'))
	return render_template('login.html' , error = None)

@app.route('/logout')
@login_required
def logout():
	app.redis.set(session['user'] , "0")
	session.pop('user' , None)
	return redirect(url_for('index'))

class GRID:
	def __init__(self , row , col):
		self.r = row		#rows in grid
		self.c = col		#columnds in grid
		#empty grid of rXc
		self.grid = [["Colourless" for _ in xrange(col + 1)] for _ in xrange(row + 1)]
		self.ranklist = {}
		self.conquered = 0
	#check if it is a valid access
	def valid(self , row , col):
		#invalid grid access
		if col < 0 or row < 0 or row >= self.r or col >= self.c:
			return False
		if self.grid[row][col] != "Colourless":		#Previously occupied by a player
			return False
		return True

#mapping of all game boards from their game ID's
allBoards = {}
updErrMessage = []
updErrMessage.append("")

@app.route('/update/', methods=['GET'])
def update():
	try:
		ret_data = {
			"x": request.args.get('x'),
			"y": request.args.get('y'),
			"gameID" : request.args.get('gameID'),
			"username" : request.args.get('username')
		}
		gameID = ret_data['gameID']
		if allBoards[gameID].conquered == allBoards[gameID].r * allBoards[gameID].c:
			updErrMessage[0] = "Game already completed"
			return 'Success'
		rkey = "gameID" + gameID
		if app.redis.get(rkey) == "1":
			updErrMessage[0] = "Board frozen"
			return 'Error'
		app.redis.set(rkey , 1)
		app.redis.expire(rkey , 10)		#redis key will expire in 10 seconds disallowing anyone to make a move
		x = int(ret_data['x'])
		y = int(ret_data['y'])
		if allBoards[gameID].valid(x , y):
			allBoards[gameID].grid[x][y] = ret_data['username']
			allBoards[gameID].conquered += 1
			if ret_data['username'] in allBoards[gameID].ranklist:
				allBoards[gameID].ranklist[ret_data['username']] += 1
			else:
				allBoards[gameID].ranklist[ret_data['username']] = 1
	except:
		updErrMessage[0] = "Server unable to process request"
		return 'Error'
	updErrMessage[0] = "Request successfully handled"
	return 'Success'


@app.route('/specify' , methods = ['GET' , 'POST'])
def specify():
	if request.method == "GET":
		print "GET request"
		gameID = request.args.get('gameID')
		return render_template('specify.html' , username = session['user'] , gameID = gameID , err = None)
	try:
		print "POST recieved"
		r = int(request.form['rows'])
		c = int(request.form['columns'])
		gameID = request.form['gameID']
		allBoards[gameID] = GRID(r , c)
		return redirect(url_for('playGame' , gameID = gameID))
	except:
		err = "Invalid input"
		gameID = request.form['gameID']
		return render_template('specify.html' , username = "nope" , gameID = gameID , err = err)


@app.route('/play/<gameID>')
@login_required
def playGame(gameID):
	if gameID in allBoards:
		board = allBoards[gameID]
	else:
		return redirect(url_for('specify' , gameID = gameID))
	alive = None
	rkey = "gameID" + gameID
	if app.redis.get(rkey) == "1":
		alive = app.redis.ttl(rkey)
	return render_template('play.html' , board = board , gameID = gameID , 
										 username = session['user'] , msg = updErrMessage[0] ,
										 alive = alive , ranklist = allBoards[gameID].ranklist
						  )


@app.route('/game/create')
@login_required
def game():
	app.redis.incr("gameID")
	gameID = app.redis.get("gameID")
	return redirect(url_for('playGame' , gameID = gameID))
	

if __name__ == '__main__':
	app.redis.set("mykey" , 1)
	app.redis.set("gameID" , 0)
	app.run(debug = True , host = "0.0.0.0")