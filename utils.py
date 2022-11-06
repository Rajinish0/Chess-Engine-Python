import pygame, os
from pygame.locals import *
import pprint, copy
# from button import Button

W, H = 1000, 680
BLANK = '-'
numBoxes = 8 ## 8x8 grid.
boxW = W//numBoxes
boxH = H//numBoxes
WHITE, BLACK = (0, 1)
colors = {1:(51,51,51),0:(144,238,144)}
isWhite = lambda x : x.isupper()
isBlack = lambda x : x.islower()
toWhite = lambda x : x.upper()
toBlack = lambda x : x.lower()

funcs = {WHITE: isWhite, BLACK: isBlack}
toFuncs = {WHITE: toWhite, BLACK: toBlack}

isCurrentPlayer = lambda x, currentPlayer : funcs[currentPlayer](x)
changeToCurPlayer = lambda x, currentPlayer : toFuncs[currentPlayer](x)


defaultFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0'
ROOKE = 'r'
KNIGHT = 'n'
BISHOP = 'b'
QUEEN = 'q'
KING = 'k'
PAWN = 'p'
p = [ROOKE, KNIGHT, BISHOP, QUEEN, KING, PAWN]
players = {WHITE:'WHITE', BLACK:'BLACK'}
moveGetFuncs = lambda x :  {ROOKE:ROOKEMOVES,
						    KNIGHT:KNIGHTMOVES,
						    BISHOP:BISHOPMOVES,
						    QUEEN:QUEENMOVES,
							KING:KINGMOVES,
							PAWN:PAWNMOVES}[x]

allPieces = {WHITE: [toWhite(each) for each in p],
			  BLACK: p}

pygame.font.init()
font = pygame.font.SysFont('freesansbold.ttf', 20)


class States:
	mousePressed = False
	mouseReleased = False
	keyPressed = False
	doResetCursor = True
	saveScreen = False
	key = None

	KINGSPOS = {}
	castlingRights = {WHITE: {'queenSide': False,
							  'kingSide': False},

					  BLACK: {'queenSide': False,
					  		  'kingSide':False}}
	EnPassantRegister = []
	allPiecesPos = {}
	
	@classmethod
	def getConfig(cls):
		return {'kingspos': copy.deepcopy(cls.KINGSPOS),
				'castlingRights': copy.deepcopy(cls.castlingRights),
				'EnPassantRegister': copy.deepcopy(cls.EnPassantRegister),
				'allPiecesPos': copy.deepcopy(cls.allPiecesPos)
				}

	@classmethod
	def loadConfig(cls, cfg):
		cls.KINGSPOS = cfg['kingspos']	
		cls.castlingRights = cfg['castlingRights']
		cls.EnPassantRegister = cfg['EnPassantRegister']
		cls.allPiecesPos = cfg['allPiecesPos']				  		  



class EventHandler:
	def __init__(self, obj):
		self.obj = obj

	def render(self):
		self.obj.screen.fill((0,0,0))
		CheckEvent()
		self.draw()
		updateDisplay()

def CheckEvent():
	run = True
	States.mousePressed, States.mouseReleased, States.keyPressed= (False, )*3
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False

		if event.type == pygame.MOUSEBUTTONDOWN:
			States.mousePressed = True

		if event.type == pygame.MOUSEBUTTONUP:
			States.mouseReleased = True

		if event.type == pygame.KEYDOWN:
			States.keyPressed = True
			setKeyPressed(event)

	return run

def loadImage(imagePath):
	return pygame.image.load(image)

def loadPicsDict():
	d = {} ## FOR PYGAME.SURFACE
	l = ['black','white']
	for i,tranche in enumerate(l):
		for each in os.listdir(tranche):
			piece = each.split('.')[0]
			piece = piece.capitalize() if i > 0 else piece
			image = pygame.image.load(tranche+'\\'+each)
			image = pygame.transform.scale(image,(100,100))
			d[piece] = image
	return d

def mousePressed():
	return States.mousePressed

def mouseReleased():
	return States.mouseReleased

def keyIsPressed():
	return States.keyPressed

def getEvent():
	return States.key

def saveScreen(screen, path):
	States.saveScreen= True
	States.screen = screen
	States.impath = path

def saveImage():
	if States.saveScreen:
		pygame.image.save(States.screen, 
						  States.impath)
		States.saveScreen = False

def setKeyPressed(k):
	States.key = k

def getKingsPos(K):
	return States.KINGSPOS[K]

def addToRegister(pos):
	States.EnPassantRegister.append(pos)

def EnPassantRegister():
	return States.EnPassantRegister

def toAlgebraic(pos):
	i, j = pos
	return (chr(97 + j)+str(7-i+1))

def toNormal(alg):
	j, i = alg
	i = 8 - int(i)
	j = ord(j)-97
	return (i, j)

def inRegister(pos):
	return (pos in States.EnPassantRegister)

def resetRegister():
	States.EnPassantRegister = []

def setKingsPos(K, p):
	States.KINGSPOS[K] = p

def getAllPosOfPiece(P):
	return States.allPiecesPos[P]

def updatePosOfPiece(P, pos1, pos2):
	removePosOfPiece(P, pos1)
	addPiecePos(P, pos2)

def removePosOfPiece(P, pos):
	States.allPiecesPos[P].remove(pos)

def addPiecePos(P, pos):
	States.allPiecesPos.setdefault(P, [])
	States.allPiecesPos[P].append(pos)

def hasCastlingRights(player, side):
	return States.castlingRights[player][side]

def setCastlingRights(player, side, setting):
	States.castlingRights[player][side] = setting

def getStatesConfig():
	return States.getConfig()

def loadStatesConfig(cfg):
	States.loadConfig(cfg)

def canCastle(player):
	d = States.castlingRights[player]
	return (d['kingSide'] or d['queenSide'])

def updateCastlingRights(pos1, pos2,curPlayer, board):
	if not canCastle(curPlayer):
		return
	i1, j1 = pos1
	i2, j2 = pos2
	piece = board[i2][j2]

	if piece.lower() == KING:
		setCastlingRights(curPlayer, 'kingSide', False)
		setCastlingRights(curPlayer, 'queenSide', False)

	elif ( not (i2 % 7) and not (j2 % 7)):
		side = 'kingSide' if (j2 == 7) else 'queenSide'
		setCastlingRights(not curPlayer, side, False)

	elif piece.lower() == ROOKE:
		side = 'kingSide' if (j1 == 7) else 'queenSide'
		setCastlingRights(curPlayer, side, False)

def checkForCastlingMove(curPlayer, pos, board):
	i, j = pos
	if board[i][j].lower() == KING and canCastle(curPlayer):
		if hasCastlingRights(curPlayer, 'queenSide') and (j == 2):
			assert board[i][0].lower() == ROOKE ## for debugging. 
			move( (i, 0), (i, j+1), board)

		if hasCastlingRights(curPlayer, 'kingSide') and (j==6):
			assert board[i][7].lower() == ROOKE ## for debugging.
			move( (i, 7), (i, j-1), board )


def updateEnPassantRegister(piece, pos1, pos2):
	resetRegister()

	i1, j1 = pos1
	i2, j2 = pos2 

	if piece.lower() == PAWN and abs(i2 - i1) == 2:
		addToRegister(pos2)


def checkForEnPassantMove(curPlayer, pos, board):
	i, j = pos
	direc = 1 if curPlayer == BLACK else -1
	if board[i][j].lower() == PAWN and inRegister((i-direc, j)):
		removePosOfPiece(board[i-direc][j], (i-direc, j))
		board[i-direc][j] = BLANK


def checkForPawnPromotion(piece, curPlayer, pos):
	i, j = pos
	if piece.lower() == PAWN and not (i % 7):
		return True
	return False		

def preMoveOps(pos1, pos2, board):
	i, j = pos2
	p = board[i][j]

	if p != BLANK:
		removePosOfPiece(p, pos2)

	updatePosOfPiece(board[pos1[0]][pos1[1]], pos1, pos2)



def postMoveOperations(curPlayer, pos1, pos2, board):
	i, j = pos2

	checkForCastlingMove(curPlayer, pos2, board)
	updateCastlingRights(pos1, pos2, curPlayer, board)
	checkForEnPassantMove(curPlayer, pos2, board)
	updateEnPassantRegister(board[i][j], pos1, pos2)
	return checkForPawnPromotion(board[i][j], curPlayer, pos2)


def updateDisplay():
	pygame.display.update()
	if States.doResetCursor:
		resetCursor()
	States.doResetCursor = True
	saveImage()

def getMousePos():
	return pygame.mouse.get_pos()

def drawRect(screen, pos : tuple, w, h, 
			 c = (255, 255, 255),width=0, CENTER=False):

	r = Rect(pos[0],pos[1],w,h)
	if CENTER:
		r.center = pos
	pygame.draw.rect(screen, c, r,width)


def drawCircle(screen, x, y, c=(255,255,255), r=2, thick=0):
	pygame.draw.circle(screen, c, (x, y), r,thick)


def drawLine(screen, v1 : tuple,v2 : tuple, c=(255,255,255),thick=2):
	x1, y1 = v1
	x2, y2 = v2
	pygame.draw.line(screen, c, (x1,y1),
								(x2,y2), thick)

def drawText(screen, pos, text, color=(0,0,0)):
	text = font.render(text, True, color)
	textRect = text.get_rect()
	textRect.center = pos
	screen.blit(text, textRect)

def drawPiece(screen, piece, x,y):
	screen.blit(piece, (x,y))

def drawImage(screen, image, pos):
	screen.blit(image, pos)	

def changeCursor(cursor):
	pygame.mouse.set_cursor(cursor)
	States.doResetCursor = False

def resetCursor():
	pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def parseCastlingRights(rights):
	if rights == '-':
		return 

	for piece in rights:
		P = WHITE if isWhite(piece) else BLACK
		side = 'kingSide' if piece.lower() == 'k' else 'queenSide'
		setCastlingRights(P, side, True)

def parseEnPassant(curPlayer, pos):
	if pos == '-':
		return 

	i, j = toNormal(pos)
	direc = -1 if curPlayer == WHITE else 1
	addToRegister((i-direc, j))


def parseFen(board, initFen):
	lines = initFen.split('/')
	p2 = lines[-1].split(' ')
	boardPos = lines[:-1]+[p2[0]]
	p2 = p2[1:]

	for i, line in enumerate(boardPos):
		ind = 0
		for charac in line:
			try:
				ind += int(charac)
				continue
			except:
				board[i][ind] = charac
				if charac.lower() == KING: 
					setKingsPos(WHITE if isWhite(charac) else BLACK,
								(i, ind))
				addPiecePos(board[i][ind], (i, ind))
				ind += 1

	curPlayer = WHITE if p2[0] == 'w' else BLACK
	parseCastlingRights(p2[1])
	parseEnPassant(curPlayer, p2[2])

	pprint.pprint(States.__dict__)

	return (board, curPlayer)



def ROOKEMOVES(board, pos, curPlayer, depth=100, lookingFor=[]):
	A = validMoveGetter(board, pos, 1, 0, curPlayer,
						[], depth, lookingFor=lookingFor)
	B = validMoveGetter(board, pos, -1, 0, curPlayer,
						[], depth, lookingFor=lookingFor)
	C = validMoveGetter(board, pos, 0, 1, curPlayer,
						[], depth, lookingFor=lookingFor)
	D = validMoveGetter(board, pos, 0, -1, curPlayer,
						[], depth, lookingFor=lookingFor)
	return (A+B+C+D)

def BISHOPMOVES(board, pos, curPlayer, depth=100, lookingFor=[]):
	A = validMoveGetter(board, pos, 1, 1, curPlayer,
	 					[], depth, lookingFor=lookingFor)
	B = validMoveGetter(board, pos, -1, -1, curPlayer,
	 					[], depth, lookingFor=lookingFor)
	C = validMoveGetter(board, pos, 1, -1, curPlayer,
	 					[], depth, lookingFor=lookingFor)
	D = validMoveGetter(board, pos, -1, 1, curPlayer,
	 					[], depth, lookingFor=lookingFor)
	return (A+B+C+D)

def getQueenLookUps():
	return ([ROOKE, QUEEN],
			[BISHOP, QUEEN])

def QUEENMOVES(*args, lookingFor=[]):
	L1, L2 = getQueenLookUps() if lookingFor != [] else ([],)*2
	A = ROOKEMOVES(*args, lookingFor=L1) 
	B = BISHOPMOVES(*args, lookingFor=L2)
	return (A+B)

def KNIGHTMOVES(board, pos, curPlayer, lookingFor=[]):
	allValidMoves = None
	for i in range(2):
		m1 = 2 if i else 1
		m2 = 2 if not i else 1
		A = validMoveGetter(board, pos, m1*1, -m2*1, curPlayer,
		 					[], depth=1, lookingFor=lookingFor)
		B = validMoveGetter(board, pos, m1*1, m2*1, curPlayer,
		 					[], depth=1, lookingFor=lookingFor)
		C = validMoveGetter(board, pos, -m1*1, m2*1, curPlayer,
		 					[], depth=1, lookingFor=lookingFor)
		D = validMoveGetter(board, pos, -m1*1, -m2*1, curPlayer,
		 					[], depth=1, lookingFor=lookingFor)
		out = (A + B + C + D)
		allValidMoves =  out if allValidMoves is None else (out + allValidMoves)

	return allValidMoves


def KINGMOVES(board, pos, curPlayer, lookingFor=[]):
	A = ROOKEMOVES(board, pos, curPlayer, depth=1, lookingFor=lookingFor)
	B = BISHOPMOVES(board, pos, curPlayer, depth=1, lookingFor=lookingFor)
	out = A + B
	if lookingFor == [] and canCastle(curPlayer):
		C = getCastlingMoves(board, pos, curPlayer)
		out += C
	return out


def PAWNMOVES(board, pos, curPlayer, lookingFor=[]):
	moveSign = -1 if curPlayer == WHITE else 1
	numMoves = 2 if (pos[0] == 1 or pos[0] == 6) else 1

	A 	=   validMoveGetter(board, pos, 1*moveSign, 1, curPlayer, [],
						   1, True, onlyOpponent=True, lookingFor=lookingFor)
	B	=	validMoveGetter(board, pos, 1*moveSign, -1, curPlayer, [],
						   1, True, onlyOpponent=True, lookingFor=lookingFor)
	C	=	validMoveGetter(board, pos, 1*moveSign, 0, curPlayer, [],
						   numMoves, includeOpponent=False, 
						   onlyOpponent=False, lookingFor=lookingFor)
	out = (A + B + C)
	if lookingFor == []:
		out += getEnPassantMove(board, pos, moveSign, curPlayer)

	return out

def checkValidityOfEnpassant(board, pos, pos2, curPlayer, moveSign):
	if pos2 == []:
		return []
	i2, j2 = pos2[0]
	orig = board[i2-moveSign][j2]

	board[i2-moveSign][j2] = BLANK
	v = isValid(curPlayer, pos, pos2[0], board)
	board[i2-moveSign][j2] = orig

	return pos2 if v else []



def getEnPassantMove(board, pos, moveSign, curPlayer):
	i, j = pos
	out = []

	if inRegister((i, j-1)):
		out = [(i+moveSign, j-1)]

	elif inRegister((i, j+1)):
		out = [(i+moveSign, j+1)]

	return checkValidityOfEnpassant(board, pos, out, curPlayer, moveSign)	





def getCastlingMoves(board, pos, curPlayer):
	if kingInCheck(board, curPlayer): return []
	moves = validMoveGetter(board, pos, 0, 1, curPlayer,
							[], depth = 2, lookingFor= []) if hasCastlingRights(curPlayer, 'kingSide') else []
	moves2 = validMoveGetter(board, pos, 0, -1, curPlayer,
							[], depth = 3, lookingFor = []) if hasCastlingRights(curPlayer, 'queenSide') else []

	m1 = [moves[1]] if len(moves) == 2 else []
	m2 = [moves2[1]] if len(moves2) == 3 else []

	return (m1+m2)
 


def updateKingsPos(pos1, pos2, board):
	i1, j1 = pos1

	cp = WHITE if isWhite(board[i1][j1]) else BLACK
	if board[i1][j1].lower() == KING:
		setKingsPos(cp, pos2)
		# CheckForCastlingMove(cp, pos2, board)


def move(pos1, pos2, board, doOps=True):
	i1, j1 = pos1
	i2, j2 = pos2
	updateKingsPos(pos1, pos2, board)
	if doOps:
		preMoveOps(pos1, pos2, board)

	board[i2][j2] = board[i1][j1]
	board[i1][j1] = BLANK

def isValid(curplayer, orig, pos, board):
	i, j = pos
	piece = board[i][j]

	move(orig, pos, board, False)
	KiC = kingInCheck(board, curplayer)
	move(pos, orig, board, False)
	board[i][j] = piece

	return (not KiC)


def validMoveGetter(board, pos, movei, movej, curPlayer,
					allValidMoves=[], depth=100, includeOpponent=True,
					onlyOpponent=False, lookingFor=[], found=False, orig=None):
	i, j = pos
	orig = orig or pos
	i+= movei; j+= movej ## THE REASON FOR DOING THIS IS THAT I DONT WANT TO INCLUDE INIT POS IN THE FINAL VALID MOVES.
	depth -= 1

	if (i >= 8 or i < 0 or j >= 8 or j < 0 or
		isCurrentPlayer(board[i][j], curPlayer) or depth <= -1):
		return found if lookingFor != [] else allValidMoves

	'''
	the extra complexity is because of the pawn, it can not move forward
	if there is opponent and can only move in the diag if there's an opponent,
	so if board[i,j] is empty, then I check if Im not in the onlyOpponent mode
	which is used for checking diagonals of the pawn.
	On the the other hand if board[i,j] is not empty i.e there's an opponent
	then I have to be in onlyOpponent mode which is activated during the diagonal check ups.
	or in includeOpponent mode, which is the normal mode.
	'''
	if ((board[i][j] != BLANK and (includeOpponent or onlyOpponent)) or 
		(board[i][j] == BLANK and (not onlyOpponent))):
		found = True if board[i][j].lower() in lookingFor else found
		if not lookingFor and isValid(curPlayer, orig, (i,j), board): ## if moving curplayer from orig to i,j is valid on this board
			allValidMoves.append((i,j))


	if board[i][j] != BLANK:
		return found if lookingFor != [] else allValidMoves

	return validMoveGetter(board, (i, j), movei, movej, 
						   curPlayer, allValidMoves, depth, includeOpponent,
						   lookingFor=lookingFor, found=found, orig=orig)


def getValidMoves(piece, pos, curPlayer, board):
	return moveGetFuncs(piece)(board, pos, curPlayer)


def generateBoard(initFen):
	board = [[BLANK for i in range(numBoxes)]
			 for j in range(numBoxes)]
	return parseFen(board, initFen)



def kingInCheck(board, curPlayer):
	kPos = getKingsPos(curPlayer)
	fin =  (QUEENMOVES(board, kPos, curPlayer, lookingFor=[QUEEN, BISHOP, ROOKE]) or 
			PAWNMOVES(board, kPos, curPlayer, lookingFor=[PAWN]) or 
			KNIGHTMOVES(board, kPos, curPlayer, lookingFor=[KNIGHT]) or 
			KINGMOVES(board, kPos, curPlayer, lookingFor=[KING]) )
	return (fin > 0)

def isPossibleToMove(board, curPlayer):
	for piece in allPieces[curPlayer]:
		if piece.lower() == KING: 
			continue
		for pos in getAllPosOfPiece(piece):
			Moves = moveGetFuncs(piece.lower())(board, pos, curPlayer)
			if Moves:
				return True
	return False


	# for i in range(numBoxes):
	# 	for j in range(numBoxes):
	# 		curPiece = board[i][j]
	# 		if curPiece != BLANK and curPiece.lower() != KING and isCurrentPlayer(curPiece, curPlayer):
	# 			Moves = moveGetFuncs(curPiece.lower())(board, (i,j), curPlayer)
	# 			if Moves:
	# 				return True
	# return False


def hasNoMoves(board, curPlayer):
	possibleMoves = KINGMOVES(board, getKingsPos(curPlayer), curPlayer)
	if possibleMoves == []:
		if isPossibleToMove(board, curPlayer):
			return False
		else:
			return True
	return False



def getAllPossibleMoves(curPlayer, board):
	allPossibleMoves = {}

	for piece in allPieces[curPlayer]:
		for pos in getAllPosOfPiece(piece):
			allPossibleMoves[pos] = getValidMoves(piece.lower(), pos, curPlayer, board)

	# for i in range(numBoxes):
	# 	for j in range(numBoxes):

	# 		if isCurrentPlayer(board[i][j], curPlayer):
	# 			allPossibleMoves[(i, j)] = getValidMoves(board[i][j].lower(), (i,j),
	# 						  							 curPlayer, board) 
	return allPossibleMoves




