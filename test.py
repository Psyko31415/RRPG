import pygame, sys, math
from pygame.locals import *

screen_width = 500
screen_height = 500

white = (255,255,255)
gray = (75,75,75)
red = (255,0,0)

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
screen.convert()

def quit():
	pygame.quit()
	sys.exit()
	
def negative(x):
	if x != 0:
		return(int(x/abs(x)))
	else:
		return(1)

def angleFix(pos, angle, centerPos): #True angle, 0 - 360 from 0 - 90 and a center pos 
	if pos[0] > centerPos[0] and pos[1] < centerPos[1]:
		angle = abs(90 - angle) + 90
	elif pos[0] > centerPos[0] and pos[1] > centerPos[1]:
		angle += 180
	elif pos[0] < centerPos[0] and pos[1] > centerPos[1]:
		angle = abs(90 - angle) + 270
	return(angle)
	
def draw_eye(angle, length):
	r = (eye_back_rect.w - eye_lens_rect.w)/2
	l1 = math.cos(math.radians(angle)) * r
	l2 = math.sin(math.radians(angle)) * r
	
	eye_lens_rect.center = (eye_back_rect.center[0] + l1 * negative(length[0]), eye_back_rect.center[1] + l2 * negative(length[1]))
	
	screen.blit(eye_back, (eye_back_rect.x, eye_back_rect.y))
	screen.blit(eye_lens, (eye_lens_rect.x, eye_lens_rect.y))

def main_loop():
	global eye_proj_speed
	eye_fire = False
	eye_proj_noChase = False
	
	img = pygame.image.load("spikes.png")
	
	while True:
		
		screen.fill(gray)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and not eye_fire:
					eye_fire = True
					eye_proj_rect.center = (screen_width/2, screen_height/2)
					eye_proj_speed = [multi * negative(length[0]), yinx * multi * negative(length[1])]
				if event.key == pygame.K_q:
					quit()
		
		
		screen.blit(img, (0,0))
		img = img.convert_alpha()
		img.set_alpha(255)
		
		screen.blit(img, (100,100))
		
		pygame.display.update()
		clock.tick(30)
		
main_loop()