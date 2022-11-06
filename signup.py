from button import *
import sqlite3, sys


con = sqlite3.connect('Chess.db')
c = con.cursor()
bgImage = 'sprites\\background.jpg'
loginImage = 'sprites\\login.jpg'
levelImage = 'sprites\\level.jpg'


# RUN ONLY FIRST TIME,
# UNCOMMENT if database is not created.

# c.execute("""CREATE TABLE players (
# 			username text,
# 			password text,
# 			level int,
# 			initfen text
# 		)""")

def loadImage(path, w, h):
	im = pygame.image.load(path)
	im = pygame.transform.scale(im, (w, h))
	return im	


class Database:


	def insert(username, password, level, initfen):
		c.execute("INSERT INTO players VALUES ('{}', '{}', '{}', '{}')".format(username, 
																			   password, level,
															 	  			   initfen))
		con.commit()


	'''
	TO DO:
	THIS QUERY WAY IS PRONE TO SQL INJECTION,
	but I don't really care about that.
	'''
	def get_by_username(username):
		c.execute("SELECT * FROM players WHERE username='{}'".format(username))
		return c.fetchone()

	def get_by_username_and_level(username, level):

		c.execute("SELECT * FROM players WHERE username='{}' and level={}".format(username,
																				  level))
		return c.fetchone()

	def update_fen(username, level, fen):
		c.execute("UPDATE players SET initfen='{}' WHERE username='{}' and level={}".format(fen, 
																					username, level) )

		con.commit()



class loginScreen():

	def __init__(self, screen):
		self.run = True
		self.screen = screen
		self.bg = loadImage(bgImage, W, H)
		self.buttons = [Button((736, 415), 157, 60,
								name='signup', draw=False), 
						Button((741, 500), 147, 63, 
								name='login', draw=False) ]



	def handleButtons(self):
		for button in self.buttons:
			button.draw(self.screen)
			if button.clicked:
				return button.name

	def draw(self):
		self.screen.fill((0,0,0))
		self.screen.blit(self.bg, (0,0))

	def getType(self):
		while self.run:
			self.run = CheckEvent()
			self.draw()
			updateDisplay()
			type_ = self.handleButtons()
			if type_ != None:
				return type_
		sys.exit()



class DataEntryScreen():
	def __init__(self, screen):
		self.run = True
		self.screen = screen
		self.bg = loadImage(loginImage, W, H)
		self.nameField = TextField((507, 280), 225, 46,
									rectWidth=5, textColor=(21,21,21), draw=False)
		self.passField = TextField((507, 423), 225, 46,
									rectWidth=5, textColor=(21,21,21), draw=False)
		self.EnterButton = Button((430, 478), 140, 50, draw=False)
		self.BackButton = Button((33, 20), 90, 40, draw=False)
		self.usernameError = ''
		self.passwordError = ''

	def draw(self):
		self.screen.fill((0,0,0))
		self.screen.blit(self.bg, (0,0))
		self.nameField.draw(self.screen)
		self.passField.draw(self.screen)
		self.EnterButton.draw(self.screen)
		self.BackButton.draw(self.screen)
		self.drawErrors()

	def drawErrors(self):
		drawText(self.screen, (507, 280 + 35),
				 self.usernameError, (255, 0, 0))

		drawText(self.screen, (507, 423 + 30),
				 self.passwordError, (255, 0, 0))

	def throwPasswordError(self,err):
		self.passwordError = err

	def throwUserNameError(self,err):
		self.usernameError = err

	def handleInfo(self, username, password, type_):
		success = True
		if username == '':
			self.throwUserNameError("USERNAME CAN NOT BE EMPTY")
			success = False

		if type_ == 'signup' and Database.get_by_username(username) != None:
			self.throwUserNameError("USERNAME ALREADY TAKEN") 
			success = False

		if password == '':
			self.throwPasswordError("PASSWORD CAN NOT BE EMPTY")
			success = False

		if type_ == 'login':

			if success and Database.get_by_username(username) is None:
				self.throwUserNameError("USER NOT FOUND")
				success = False
			else:
				self.throwUserNameError("")

			if success and password != Database.get_by_username(username)[1]:
				self.throwPasswordError("WRONG PASSWORD")
				success = False


		return (username, password) if success else 'N'


	def handleButtons(self, type_):
		if self.EnterButton.clicked:
			return self.handleInfo(self.nameField.text,
								   self.passField.text, type_)
		elif self.BackButton.clicked:
			return None

		else:
			return 'N'


	def getPlayerData(self,type_):
		self.__init__(self.screen)
		while self.run:
			self.run = CheckEvent()
			self.draw()
			data = self.handleButtons(type_)
			updateDisplay()
			if data != 'N':
				return data
		sys.exit()

class LevelScreen():

	def __init__(self, screen):
		self.run = True
		self.screen = screen
		self.bg = loadImage(levelImage, W, H)
		self.numlevels = 10
		self.buttons = self.createButtons()

	def createButtons(self):
		buttons = []

		width = 174
		height = 87
		spacing = 20

		for i in range(1, self.numlevels+1):
			buttons.append(Button(
						(111+ 600*(i//6) , 86+(height+spacing)*((i-1)%5)), 
						width, height,
						name=f'{i}', draw=False))
		return buttons

	def draw(self):
		self.screen.fill((0,0,0))
		self.screen.blit(self.bg, (0, 0))
		self.run = CheckEvent()
		for button in self.buttons:
			button.draw(self.screen)
		updateDisplay()
		if mousePressed():
			print(getMousePos())

	def getClick(self):
		for button in self.buttons:
			if button.clicked:
				return button.name

	def getLevel(self):
		while self.run:
			self.draw()
			L = self.getClick()
			if L is not None:
				return L
		sys.exit()




class InfoHandler():

	def __init__(self, screen):
		self.loginScreen = loginScreen(screen)
		self.dataScreen = DataEntryScreen(screen)
		self.levelSreen = LevelScreen(screen)

	def process(self, data, level, type_):
		username, password = data
		d = Database.get_by_username_and_level(username, level)


		if type_ == 'signup' or (type_ == 'login' and d is None):
			Database.insert(username, password, level, defaultFen)

		return Database.get_by_username_and_level(username, level)


	def getInfo(self):
		data = None
		while data == None:
			type_ = self.loginScreen.getType()
			data = self.dataScreen.getPlayerData(type_)
		level = self.levelSreen.getLevel()
		return self.process(data, level, type_)


# screen = pygame.display.set_mode((W, H))
# inf = InfoHandler(screen)
# print(inf.getInfo())