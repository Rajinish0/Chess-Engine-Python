from stockfish import Stockfish
from utils import toNormal




class AI:

	def __init__(self, game, level):
		self.game = game
		self.sf = Stockfish(path=r'D:\stockfish_15_win_x64\stockfish_15_x64.exe', 
							parameters={"Skill Level": level})

	def getMove(self):
		fen = self.game.generateFen()
		self.sf.set_fen_position(fen)
		bestMove = self.sf.get_best_move()
		p1, p2, promoteTo = (bestMove[:2], bestMove[2:4], bestMove[4:])
		return [toNormal(p1), toNormal(p2), promoteTo]
