## chess AI
from utils import *
clock = pygame.time.Clock()

pieceValues = {PAWN:100,
			   BISHOP:340,
			   ROOKE:500,
			   KNIGHT:325,
			   QUEEN:900}
winValues = {WHITE: -(1e6),
			 BLACK: 1e6,
			 None: 0}

def evaluateGameEnd(game):
	return winValues(game.winner)

def StaticEvaluation(game, maximizingPlayer):
	if game.gameEnd: 
		pprint.pprint(game.board)
		return winValues[game.winner]

	score = 0
	for i in range(8):
		for j in range(8):
			piece = game.board[i][j]

			if piece == BLANK: 
				continue

			elif isCurrentPlayer(piece, maximizingPlayer):
				score += pieceValues.get(piece.lower(), 0)

			else:
				score -= pieceValues.get(piece.lower(), 0)
	return score


class chessAI():
	def __init__(self, game, depth, maximizingPlayer=BLACK):
		self.game = game
		self.depth = depth
		self.maximPlayer = maximizingPlayer

	def getMove(self):
		self.bestMove = self.minMax(self.depth, float('-inf'),
									float('inf'), True)
		return self.bestMove

	def minMax(self, depth, alpha, beta, orig=False):
		if depth == 0 or self.game.gameEnd:
			return StaticEvaluation(self.game, 
									self.maximPlayer)


		allPossibleMoves = getAllPossibleMoves(self.game.curPlayer, 
											   self.game.board)

		if self.game.curPlayer == self.maximPlayer:
			highest = float('-inf')
			bestMove = None

			for pos1, movesOfPos1 in allPossibleMoves.items():
				for pos2 in movesOfPos1:
					cfg = self.game.getConfig()
					self.game.makeMove(pos1, pos2, dontCheck=True)
					score = self.minMax(depth-1, alpha, beta)

					self.game.loadConfig(cfg)

					if ( score > highest ):
						highest = score
						bestMove = [pos1, pos2]
					alpha = max(score, alpha)

					if alpha >= beta:
						return highest;

			return bestMove if orig else highest

		elif self.game.curPlayer != self.maximPlayer:
			lowest = float('inf')
			for pos1, movesOfPos1 in allPossibleMoves.items():
				for pos2 in movesOfPos1:

					cfg = self.game.getConfig()

					self.game.makeMove(pos1, pos2, dontCheck=True)
					score = self.minMax(depth-1, alpha, beta)

					self.game.loadConfig(cfg)

					lowest = min(score, lowest)

					beta = min(score, beta)
					if alpha >= beta:
						return lowest

			return lowest