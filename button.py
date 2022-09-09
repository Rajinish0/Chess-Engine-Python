from utils import *
import random

class Button:


	def __init__(self, pos, width, height,
				 imagePath=None, name='', color=(21, 21, 21),
				 textColor=(255, 255, 255), rectWidth=0, draw=True):
		print(pos, width, height, imagePath)
		self.pos = pos
		self.w = width
		self.h = height
		self.image = self.loadImage(imagePath)
		self.name = name
		self.color = color
		self.RectWidth = rectWidth
		self.textColor = textColor
		self.cursor = pygame.SYSTEM_CURSOR_HAND
		self.clicked = False 
		self.d = draw


	def loadImage(self, imagePath):
		if imagePath is None:	return None
		img = pygame.image.load(imagePath)
		img = pygame.transform.scale(img, (self.w, self.h))
		return img


	def inBound(self, x, y):
		px, py = self.pos
		return ( ( (px)<=x<=(px+self.w) ) and 
			   	 ( (py)<=y<=(py+self.h) ) )


	def checkIfClicked(self):
		self.clicked = False
		x, y = getMousePos()
		if self.inBound(x,y):
			changeCursor(self.cursor)
			if mousePressed():
				self.clicked = True


	def draw(self, screen):
		self.checkIfClicked()

		if self.d:
			if self.image is not None:
				drawImage(screen, self.image, self.pos)
			else:
				drawRect(screen, self.pos, self.w, self.h,
						 c=self.color, width=self.RectWidth)


class TextField(Button):
	def __init__(self, *args, **kwargs):
		super().__init__(*args,**kwargs)
		self.text = ''
		self.cursor = 0
		self.done = False
		self.cursor = pygame.SYSTEM_CURSOR_IBEAM

	def inBound(self, x, y):
		px, py = self.pos
		return ( ( (px-self.w/2)<=x<=(px+self.w/2) ) and 
			   	 ( (py-self.h/2)<=y<=(py+self.h/2) ) )		

	def checkIfClicked(self):
		x, y = getMousePos()
		if mousePressed():
			if self.inBound(x,y):
				self.clicked= True
			else:
				self.clicked = False

	def handleWrite(self):
		if self.clicked:

			if keyIsPressed():
				event = getEvent()

				if event.key == pygame.K_RETURN:
					self.done = True
					self.clicked = False

				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:self.cursor][:-1]+self.text[self.cursor:]
					self.cursor -= 1

				elif event.key == pygame.K_LEFT:
					self.cursor -= 1

				elif event.key == pygame.K_RIGHT:
					self.cursor += 1

				else:
					self.text = self.text[:self.cursor]+event.unicode+self.text[self.cursor:]
					self.cursor += 1

				self.cursor = min(len(self.text), self.cursor)
				self.cursor = max(0, self.cursor)


	def drawText(self, screen):
		if self.d:
			drawRect(screen, self.pos, self.w, self.h,
					 c=self.color, width=self.RectWidth,
					 CENTER=True)
		T = (self.text[:self.cursor]+'|'+self.text[self.cursor:]) if self.clicked else self.text
		drawText(screen, self.pos, T,
				 self.textColor)

	def draw(self, screen):
		self.checkIfClicked()
		self.handleWrite()
		self.drawText(screen)





class PawnPromotionHandler():
	def __init__(self, game):
		self.game = game
		self.w, self.h = 100, 100
		self.spacing = 50
		self.buttons = self.createButtons()

	def createButtons(self):
		buttons = {BLACK:[],
				   WHITE:[]}
		startX = W//2 - ((self.w)*4 + (self.spacing)*3)//2


		for player in [BLACK, WHITE]:
			path = 'black' if player == BLACK else 'white'

			for i, piece in enumerate([QUEEN, ROOKE,
									   BISHOP, KNIGHT]):

				imagePath = path+'\\'+piece+'.png'
				buttons[player].append( Button(
						(startX + i*(self.w+self.spacing), H//2 - self.h//2 ),
						self.w, self.h, imagePath=imagePath, name=piece  
					) )
		return buttons

	def drawButtons(self):
		for button in self.buttons[self.game.curPlayer]:
			button.draw(self.game.screen)

	def checkForClick(self):
		for button in self.buttons[self.game.curPlayer]:
			if button.clicked:
				return button.name
		return None

	def getSelection(self):
		while True:
			self.game.screen.fill((0,0,0))
			CheckEvent()
			self.game.draw()
			self.drawButtons()
			updateDisplay()
			S = self.checkForClick()
			if S is not None:
				return S


