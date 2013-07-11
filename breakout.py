import os, sys, pygame, random
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'

size = width, height = 300, 400
black = 0,0,0
highscore = 0
number_of_blocks = 12

def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'cannot load image:', name
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
			image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()


class Ball(pygame.sprite.Sprite):
	"""moves a ball across the screen"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('ball.bmp',-1)
		self.rect.midtop = width, height
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.speed = [0,0]
		self.stuck = 1

	def update(self):
		if self.stuck:
			speed = [0,0]
			self.rect.midtop = pygame.mouse.get_pos()[0], height-83
		else:
			self.walk()

	def unstuck(self, speed = [2, -2]):
		self.stuck = 0
		self.speed = speed

	def bounce(self, bar):
		dampener = 4
		max_speed = 7
		# Changes ball's horizontal speed according to where it strikes the bar
		self.speed = [min((self.rect.midtop[0] - bar.rect.midtop[0])/dampener, max_speed), -self.speed[1]]

	def hit_block(self):
		self.speed = [self.speed[0], -self.speed[1]]


	def walk(self):
		"moves the ball across the screen, ball disappears at the bottom"
		self.rect = self.rect.move(self.speed)
		if self.rect.left < 0:
			self.rect.left = 1 # Avoid ball getting stuck on left edge
			self.speed[0] = -self.speed[0]
		elif self.rect.right > width:
			self.rect.right = width-1 # Avoid ball getting stuck on right edge
			self.speed[0] = -self.speed[0]

		if self.rect.top < 0:
			self.speed[1] = -self.speed[1]
		if self.rect.bottom > height:
			self.kill()


class Bar(pygame.sprite.Sprite):
	"the bar at the bottom of the screen"
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image = pygame.Surface([50, 10])
		self.image.fill([200,200,200])
		self.rect = self.image.get_rect()
		self.rect.midtop = width/2, height-20
	
	def update(self):
		"move the bar according to mouse position"
		mousepos = pygame.mouse.get_pos()[0]
		self.rect.midtop = mousepos, height-50


class Block(pygame.sprite.Sprite):
	"blocks that the player aims to hit"
	def __init__(self, color, width, height, pos):
		pygame.sprite.Sprite.__init__(self)

		# Create block image and fill it with a color
		self.image = pygame.Surface([width, height])
		self.image.fill(color)

		# Fetch the rectangle object that has the dimensions of the block
		self.rect = self.image.get_rect()
		self.rect.midtop = pos

	def update(self):
		pass

class Score(pygame.sprite.Sprite):
	"displays the score"
	def __init__(self, score=0, color = (100,200,100)):
		pygame.sprite.Sprite.__init__(self)
		self.score = score
		self.font = pygame.font.Font(None, 20)
		self.color = color
		self.image = self.font.render(str(score) + "  Highscore = " + str(highscore), True, self.color)
		self.rect = self.image.get_rect()
		self.rect.center = size[0]/2, 9


	def add_score(self, amount):
		self.score = self.score + amount

	def update(self):
		global highscore
		oldtopleft = self.rect.topleft
		self.image = self.font.render(str(self.score) + "  Highscore = " + str(highscore), True, self.color)
		self.rect = self.image.get_rect()
		self.rect.topleft = oldtopleft
		if self.score > highscore:
			highscore = self.score


class Start(pygame.sprite.Sprite):
	"displays 'How many blocks this time?"
	def __init__(self, color = (100,200,100)):
		pygame.sprite.Sprite.__init__(self)
		self.font = pygame.font.Font(None, 38)
		self.color = color
		self.image = self.font.render("Click to play", True, self.color)
		self.rect = self.image.get_rect()
		self.rect.midtop = size[0]/2, size[1]/2

	def update(self):
		self.kill()

def main():
	global number_of_blocks
	pygame.init()
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("Breakout")
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(black)
	clock = pygame.time.Clock()

	def game_loop():
		done = False
		multiplier = 1
		while not done:
			clock.tick(60)

			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
				elif event.type == MOUSEBUTTONDOWN:
					if ball.stuck:
						ball.unstuck()

			if pygame.sprite.collide_rect(bar, ball):
				ball.bounce(bar)
				multiplier = 1

			hitblocks = pygame.sprite.spritecollide(ball, blocks, True)
			if hitblocks:
				ball.hit_block()
				score.add_score(50*len(hitblocks)*multiplier)
				multiplier += 1

			allsprites.update()
			screen.blit(background, (0,0))
			allsprites.draw(screen)
			pygame.display.flip()
			if ball and not blocks:
				game_over(True)
				return main()
			elif not ball in allsprites:
				game_over(False)
				return main()


	def intro_screen():
		start = Start()
		startsprite = pygame.sprite.RenderPlain(start)
		screen.blit(background, (0,0))
		startsprite.draw(screen)
		pygame.display.flip()
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
				if event.type == MOUSEBUTTONDOWN:
					return True


	def game_over(win):
		global number_of_blocks
		if win:
			message = 'You Win!'
			number_of_blocks += 2
		else:
			message = 'Game Over'
		for e in allsprites:
			if e is not score: e.kill()
		font = pygame.font.Font(None, 80)
		text = font.render(message,  1, (100,200,100))
		textpos = text.get_rect()
		textpos.midtop = size[0]/2, size[1]/2
		screen.blit(text, textpos)
		pygame.display.flip()
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
				if event.type == MOUSEBUTTONDOWN:
					main()


	def initialize_pieces():

		ball = Ball()
		bar = Bar()
		score = Score()
		blocks = pygame.sprite.Group()
		def create_blocks(quantity, width=50, height=20):
			for num in range(quantity):
				color = (random.randint(10,255),random.randint(10,255),
							random.randint(10,255))
				# Create blocks in the given space
				block = Block(color, width, height, (((num*width)%size[0])+width/2,
							20 + (num/(size[0]/width))*height))
				blocks.add(block)
		board = create_blocks(number_of_blocks)
		allsprites = pygame.sprite.RenderPlain((ball, bar, blocks, score))
		return ball, bar, score, blocks, board, allsprites

	if intro_screen():

		if pygame.font:
			font = pygame.font.Font(None, 20)
			text = font.render("Score = ",  1, (100,200,100))
			textpos = text.get_rect()
			background.blit(text, textpos)

		ball, bar, score, blocks, board, allsprites = initialize_pieces()
		game_loop()


if __name__ == '__main__': main()



