from button import * 
from ai import AI
import os
## default const variables.


'''
for getting a valid move, I create a generic validMoveGetter function
it gets a movei and a movej, and will move in that direction until 
it sees a player of it's own, is out of the board, or hits a player of 
the opposite side. It will not add current position to the list of validMoves
if by moving there it'll cause the king of the currentPlayer to be in Check.
'''


'''
For En Passant I create a register that gets emptied after a move is made.
If a move is made and it's a pawn and it's moving two steps, it gets added to the
register. Then at the time of getting valid moves for pawn I check if
the right or left box of the pawn are in the EnPassantRegister, if 
yes I simply add one box below(or above) to the valid moves.
checks for kingInCheck are also done here.
'''

'''
Castling is implimented in a simple way, right rooke moves king side castling rights are gone
and so on and so forth. To get valid moves for the king for castling
what I do is I go into validMoveGetter, which requires movei and movej
I give it a movej of 1 (for kingside castling if it has the rights)
and if it returns me a list of 2 possible moves on that side,
Then that means I can castle on the side. The sole reasong for doing this 
lengthy process is that a king can not castle through a check or into a check
So since validMoveGetter already checks if moving into that position would cause
the king to be in check, if I were to castle through a check or into a check
validMoveGetter in this case would return less than 2 positions.
'''


'''
To detect for Check Im using moving a piece's moves from the king's position
and checking if that piece is there, that obv means that the king is in check. 
To avoid writing a different function for this, I used validMoveGetter, 
I simply added a lookingFor argument and in this case it returns a 
value of True or False if it found the value in lookingFor list.
'''


'''
To detect a CheckMate, first it's checked if the king is in Check.
Next, I get king's moves, if it can move than obv it's not CheckMate.
If the king can't move, (I think) there's no other way than to check if any other piece
can move, so I do that.
'''


def genDict(board):
	d = {}
	for i in range(8):
		for j in range(8):
			P = board[i][j]
			if P == BLANK: 
				continue
			d.setdefault(P, [])
			d[P].append((i,j))
	return d

def isEqual(d1, d2):
	S = True
	for key, value in d1.items():
		S = (S and (set(list(value)) == set(d2[key]) ))
	return S


class Chess:
	def __init__(self, screen, info, initFen=defaultFen, initPlayer=WHITE):
		self.screen = screen
		(self.username, _, self.level, self.initFen) = info
		self.board, self.curPlayer = generateBoard(self.initFen)
		self.run = True
		self.images = loadPicsDict()
		self.pieceInHand = None
		self.validMoves = []
		self.inCheck = None
		self.gameEnd = False
		self.pawnPromotionHandler = PawnPromotionHandler(self)
		self.chessAI = AI(self, self.level)
		self.path = f'Games\\{self.username}'
		self.createPath()
		self.p1, self.p2 = (None, )*2
		self.count = 1

	def drawBoard(self):
		curColor = 0

		for i in range(0, W, boxW):
			for j in range(0, H, boxH):

				## draw the background
				drawRect(self.screen, (i, j), boxW, boxH, c=colors[curColor])
				curColor = not curColor

				## draw the piece
				piece = self.board[j//boxH][i//boxW]
				if piece != BLANK:
					drawPiece(self.screen, 
							  self.images[piece], 
							  i+10, j-10)

			curColor = not curColor

	def drawValidMoves(self):
		if self.pieceInHand is not None:
			i, j = self.pieceInHand
			drawRect(self.screen, (j*boxW, i*boxH), boxW, boxH,
					 c = (181, 181, 0), width=5)

		for each in self.validMoves:
			i, j = each
			drawRect(self.screen, (j*boxW, i*boxH), boxW, boxH,
					 c=(181, 0, 181), width=5)
	def drawCheck(self):
		if self.inCheck is not None:
			i, j = self.inCheck
			COLOR = (181, 0, 0) if not self.gameEnd else (181, 181, 0)
			drawRect(self.screen, (j*boxW, i*boxH), boxW, boxH,
					 c =COLOR, width = 5)

	def drawMove(self):
		if self.p1 != None:
			i, j = self.p1 
			i2, j2 = self.p2
			drawRect(self.screen, (j*boxW, i*boxH), boxW, boxH,
			 c = (81, 0, 0), width = 5)

			drawRect(self.screen, (j2*boxW, i2*boxH), boxW, boxH,
			 c =(51, 0, 0), width = 5)


	def draw(self):
		self.drawBoard()
		self.drawMove()
		self.drawValidMoves()
		self.drawCheck()


	def createPath(self):
		if not os.path.exists(self.path):
			os.mkdir(self.path)
		else:
			for each in os.listdir(self.path):
				os.remove(os.path.join(self.path, each))

	def getConfig(self):
		d = {
			'board': copy.deepcopy(self.board),
			'curPlayer': copy.deepcopy(self.curPlayer),
			'pieceInHand': copy.deepcopy(self.pieceInHand),
			'validMoves': copy.deepcopy(self.validMoves),
			'inCheck': copy.deepcopy(self.inCheck),
			'gameEnd': copy.deepcopy(self.gameEnd)
		}
		return [d,
				getStatesConfig()]

	def loadConfig(self, cfg):
		myCfg, statesCfg = cfg
		'''
		TO DO:
		shorter form 
		for key, value in myCfg.items():
			self.__dict__[key] = value;
		even shorter is to just somehow remove the pygame surfaces from
		the local variables, and than copy self.__dict__ 
		'''
		self.board = myCfg['board']
		self.curPlayer = myCfg['curPlayer']
		self.pieceInHand = myCfg['pieceInHand']
		self.validMoves = myCfg['validMoves']
		self.inCheck = myCfg['inCheck']
		self.gameEnd = myCfg['gameEnd']


		loadStatesConfig(statesCfg)

	def copyBoard(self):
		return copy.copy(board)


	def handleMouse(self):
		self.run = CheckEvent()
		mx, my = getMousePos()
		j, i = mx//boxW, my//boxH

		if mousePressed() and not self.gameEnd:
			if self.pieceInHand is None:
				self.handlePress(i, j)
			else:
				self.makeMove(self.pieceInHand, (i, j))

	def handleAiTurn(self):
		if (self.curPlayer == BLACK):
			bestMove = self.chessAI.getMove()

			if bestMove != None:

				p1, p2, promoteTo = bestMove
				print(promoteTo)
				self.makeMove(p1, p2, dontCheck=True, selec=promoteTo)


	def handlePress(self,i, j):
		if (self.board[i][j] != '-' and
			isCurrentPlayer(self.board[i][j], self.curPlayer)):

			self.validMoves = getValidMoves(self.board[i][j].lower(), (i, j),
										 	self.curPlayer, self.board)

			self.pieceInHand = (i,j)

	def handlePromotion(self, needsPawnPromotion, pos, selec):
		if needsPawnPromotion:
			piece = (selec if selec != '' else self.pawnPromotionHandler.getSelection())
			P = changeToCurPlayer(piece, 
							  	  self.curPlayer)
			i, j = pos
			removePosOfPiece(self.board[i][j], pos)
			addPiecePos(P, pos)
			self.board[i][j] = P

	def switchPlayer(self):
		self.curPlayer = not self.curPlayer			

	def checkForCheck(self):
		isInCheck = kingInCheck(self.board, 
							  self.curPlayer)
		if isInCheck:
			self.inCheck = getKingsPos(self.curPlayer)
			return True
		return False

	def resetConfig(self):
		self.pieceInHand = None
		self.validMoves = []

	def makeMove(self, piece, pos, dontCheck=False, selec=''):
		i, j = pos
		if (dontCheck) or ((i,j) in self.validMoves):
			self.inCheck = None
			move(piece, pos, self.board)
			needsPawnPromotion = postMoveOperations(self.curPlayer, 
							   						piece, pos,
							   						self.board)
			self.handlePromotion(needsPawnPromotion, pos, selec)
			self.switchPlayer()
			self.checkForGameEnd()
			self.p1, self.p2 = (piece, pos)
			
		self.resetConfig()
		saveScreen(self.screen, 
				   self.path+f'\\{self.count}.jpg')
		self.count += 1

	def checkForGameEnd(self):
		c = self.checkForCheckMate()
		self.checkForStaleMate(c)

	def checkForStaleMate(self, check):
		if not check and hasNoMoves(self.board, self.curPlayer):
			self.gameEnd = True
			self.winner = None
			print("No one one")
		
	def checkForCheckMate(self):
		if not self.checkForCheck(): return False
		K = hasNoMoves(self.board, self.curPlayer)
		if K:
			self.gameEnd = True
			self.winner = not self.curPlayer
			print(players[self.winner] + " WON.")
		return True

	def generateFen(self):
		fen = ''

		for i in range(numBoxes):
			C = 0
			for j in range(numBoxes):
				if self.board[i][j] != BLANK:
					fen = (fen + str(C) if C != 0 else fen)
					fen += self.board[i][j]
					C = 0
					continue

				C += 1
			fen = (fen + str(C) if C != 0 else fen)
			fen += '/'
		fen = fen[:-1]
		fen += ' '

		fen += players[self.curPlayer][0].lower()
		fen += ' '

		if (not canCastle(WHITE) and not canCastle(BLACK)):
			fen += '-'
		else:
			fen += ('K' if hasCastlingRights(WHITE, 'kingSide') else '')
			fen += ('Q' if hasCastlingRights(WHITE, 'queenSide') else '')
			fen += ('k' if hasCastlingRights(BLACK, 'kingSide') else '')
			fen += ('q' if hasCastlingRights(BLACK, 'queenSide') else '')

		fen += ' '

		EPR = EnPassantRegister()
		if EPR != []:
			i, j = EPR[0] 
			direc = -1 if self.curPlayer == WHITE else 1
			fen += ( toAlgebraic( (i+direc, j ) ) )
		else:
			fen += '-'

		fen += ' '
		fen += '3'
		fen += ' '
		fen += '3'
		return fen



	def gameLoop(self):
		while self.run:
			self.screen.fill((0,0,0))
			self.handleMouse()
			self.draw()
			updateDisplay()
			self.handleAiTurn()


		
