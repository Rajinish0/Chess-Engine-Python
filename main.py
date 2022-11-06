from Chess import *
from signup import *
import cv2

image_folder = 'Games'
video_name = 'video.avi'



def makeVideo(image_folder):
	images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
	images.sort(key=lambda x: int(x.split('.')[0]))
	print(images)
	frame = cv2.imread(os.path.join(image_folder, images[0]))
	height, width, layers = frame.shape

	video = cv2.VideoWriter(os.path.join(image_folder, 
										 video_name), 0, 1, (width,height))

	for image in images:
		video.write(cv2.imread(os.path.join(image_folder, image)))
		os.remove(os.path.join(image_folder, image))

	cv2.destroyAllWindows()
	video.release()


class Game:
	def __init__(self):
		screen = pygame.display.set_mode((W,H))
		info = InfoHandler(screen).getInfo()
		self.chessGame = Chess(screen, info)

	def play(self):
		self.chessGame.gameLoop()
		if not self.chessGame.gameEnd:
			Database.update_fen(self.chessGame.username, 
							self.chessGame.level,
							self.chessGame.generateFen())
		self.makeVid()

	def makeVid(self):
		makeVideo(image_folder+f'\\{self.chessGame.username}')

g = Game()
g.play()
