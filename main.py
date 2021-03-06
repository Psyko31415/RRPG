#börja dela upp alla fienders beteenden i klasser, för tex rörelse och attacker
import pygame, sys, glob, random, math, time
from pygame.locals import *

pygame.init()

white = (255,255,255)
black = (0,0,0)
red = (200,0,0)
green = (0,200,0)
blue = (0,0,200)
light_red = (255,0,0)
light_green = (0,255,0)
light_blue = (0,0,255)
gray = (55,55,55)
light_gray = (75,75,75)
gold = (255, 215, 0)
yellow = (200,200,0)
light_yellow = (255,255,0)
purple = (128,0,128)

hands = [(44,41),(46,35),(41,57),(39,57),(50,26),(42,21)]
attack_img_size = (58,88)
units_size = 100

gameDisplay = pygame.display.set_mode((1000,800))
dis_width, dis_height = gameDisplay.get_size()
clock = pygame.time.Clock()
pygame.display.set_caption("RRPG")

FPS = 30

class Physics():	
	def sides(self, var = 10):
		self.side_left = pygame.Rect((self.x, self.y, var, self.h))
		self.side_right = pygame.Rect((self.x + self.w, self.y, -var, self.h))
		self.side_top = pygame.Rect((self.x, self.y, self.w, var))
		self.side_bottom = pygame.Rect((self.x, self.y + self.h, self.w, -var))
	
	def gravity(self, floors):
		floor_collision = False
		for floor in floors:
			if self.collide(self_part = self.side_bottom, other_part = floor.side_top): 
				floor_collision = True
			if self.y + self.h < floor.y < self.y + self.h + self.speed[1] and ((floor.x < self.x < floor.x + floor.w or floor.x < self.x +self.w < floor.x + floor.w) or (floor.x < self.x + self.speed[0] < floor.x + floor.w or floor.x < self.x + self.w + self.speed[0] < floor.w)):
				floor_collision = True
				self.y = floor.y - self.h

		if not floor_collision:
			self.speed[1] += self.grav_force
		elif self.speed[1] > 0:
			self.speed[1] = 0
		return(floor_collision)

	def collide(self, other = None, self_part = None, other_part = None):
		if self_part == None:
			if other.y < self.y < other.y + other.h or other.y < self.y + self.h < other.y + other.h or self.y < other.y < self.y + self.h or self.y < other.y + other.h < self.y + self.h:
				if self.x < other.x < self.x + self.w or self.x < other.x + other.w < self.x + self.w or other.x > self.x > other.x + other.w or other.x < self.x + self.w < other.x + other.w:
					return(True)
		else:
			if other_part.y < self_part.y < other_part.y + other_part.h or other_part.y < self_part.y + self_part.h < other_part.y + other_part.h or self_part.y < other_part.y < self_part.y + self_part.h or self_part.y < other_part.y + other_part.h < self_part.y + self_part.h:
				if self_part.x < other_part.x < self_part.x + self_part.w or self_part.x < other_part.x + other_part.w < self_part.x + self_part.w or other_part.x < self_part.x < other_part.x + other_part.w or other_part.x < self_part.x + self_part.w < other_part.x + other_part.w:
					return(True)
	
	def friction(self):
		if abs(self.speed[0]) - self.friction_force <= 0:
			self.speed[0] = 0
		else:
			self.speed[0] = (abs(self.speed[0]) - self.friction_force) * negative(self.speed[0])
		
	def connect_floors(self, floor1, floor2):
		no_return = False
		if floor1.x <= floor2.x:
			x = floor1.x
		else:
			x = floor2.x
		w = floor1.w + floor2.w
		if floor1.y == floor2.y and floor1.h == floor2.h:
			y = floor1.y
			h = floor1.h
		else:
			no_return = True
			print("Can't connect floors, Error 1: Not on same y")
		
		if not no_return:
			return(Floor(x,y,w,h))
			
	def on_floor(self, floor):
		if floor.x + self.w < self.x < floor.x + floor.w - self.w or floor.x + self.w < self.x + self.w < floor.x + floor.w - self.w:
			return(True)

class Animation():
	def ani_setup(self, ani_cd_init, path, element): 
		ani_cd = 0
		ani = glob.glob(path)
		ani.sort()
		ani_pos = 0
		ani_pos_max = len(ani) - 1
		
		try:
			self.anis.append([ani_cd_init, ani_cd, ani, ani_pos, ani_pos_max])
		except:
			self.anis = [[ani_cd_init, ani_cd, ani, ani_pos, ani_pos_max]]
			
		self.imgs[element] = pygame.image.load(ani[0])
		
		return(self.anis.index([ani_cd_init, ani_cd, ani, ani_pos, ani_pos_max]))
	
	def ani_base(self, ani_count, element):
		for i in range(len(self.anis)):
			if i != ani_count:
				self.anis[i][1] = 0
				
		self.anis[ani_count][1] -= 1
		if self.anis[ani_count][1] <= 0:
			self.anis[ani_count][1] = self.anis[ani_count][0]
			self.imgs[element] = pygame.image.load(self.anis[ani_count][2][self.anis[ani_count][3]])
			if self.anis[ani_count][3] == self.anis[ani_count][4]:
				self.anis[ani_count][3] = 0
			else:
				self.anis[ani_count][3] += 1

class Movable_object():
	def random_floor_movment(self, hero, floor):
		self.dir_cd -= 1
		if self.dir_cd == 0:
			self.dir_cd = random.randint(10, 50)
			if self.dir == -1:
				self.dir = 1
			else:
				self.dir = -1
			
		if self.stunned == 0:
			self.speed[0] = self.dir * self.walk_speed
			
	def stay_on_floor(self, floor):
		if not self.on_floor(floor):
			if abs(self.x - floor.x) < abs(self.x - (floor.x + floor.w)):
				return(1)
			else:
				return(-1)
				
class Combat():
	def knockback(self, target, dir, speed, stun, floor = 0):
		if target.unstopable == 0:
			target.speed[0] = speed[0] * dir
			target.speed[1] = speed[1]
			target.stunned = stun
			
	def recieve_dmg(self, attacker, amount, type):
		dead = False
		if type == 0:
			resist = self.armor - attacker.armor_pen
		elif type == 1:
			resist = self.magic_resist - attacker.magic_pen 
		elif type == 2:
			resist = 0
		elif type == 3:			
			self.hp_curr -= amount
			self.has_recieved_dmg = True
			if self.hp_curr <= 0:
				dead = True
			return(amount, dead)
		
		if resist < 0:
			reduce_part = 2 - 100/(100 - resist)
		else:
			reduce_part = 100/(100 + resist)
		real_amount = amount * reduce_part
		self.hp_curr -= real_amount
		self.has_recieved_dmg = True
		if self.hp_curr <= 0:
			dead = True
		return(real_amount, dead)
	
class Entity(Physics):
	def __init__(self, x, y, w, h, img, id, value):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.img = img
		self.id = id
		self.value = value
		self.speed = [0,0]
		self.grav_force = 2
		self.angle = 0
		self.sides()
		
		self.bounce_max = 5
		self.bounce_min = -self.bounce_max
		self.bounce_curr = 0
		self.bounce_dir = 1
		self.bounce_speed = 0.5
	
	def move(self, floors):
		self.sides()
		
		if self.gravity(floors):
			self.angle = 0
			self.bounce_curr += self.bounce_speed * self.bounce_dir
			if self.bounce_curr == self.bounce_max or self.bounce_curr == self.bounce_min:
				self.bounce_dir = toggle_dir(self.bounce_dir)
		else:
			self.angle += 12
			self.bounce_curr = 0
		
		self.x += self.speed[0]
		self.y += self.speed[1]
	
	def display(self):
		gameDisplay.blit(pygame.transform.rotate(self.img, self.angle), (self.x, self.y + self.bounce_curr))
	
class BaseHero(Physics, Animation, Combat):
	def __init__(self, x ,y, w, h, room_location, equips):
		
		#--- Base variables, speed ---
		
		self.id = 0
		self.x = x
		self.display_x = self.x
		self.y = y
		self.w = w
		self.h = h
		self.equips = equips
		self.grav_force = 2
		self.rect = (self.x, self.y, self.w, self.h)
		self.walk_speed = 6
		self.speed = [0,0]
		self.grav_max = 30
		self.ladder_speed = 0
		self.friction_force = 0.8
		self.speed_target = [0,0]
		self.dir = "right"
		self.sides()
		self.room_location = room_location
		self.changed_dir = False
		
		#--- Statistics --- Currently set to class "warrior"
		
		self.level = 1
		self.xp_base = 30
		self.xp_expo = 1.5
		self.hp_max = 23
		self.hp_curr = 23
		self.mp_max = 11
		self.mp_curr = 11
		self.xp_max = 30
		self.xp_curr = 0
		self.hp_base = 15
		self.mp_base = 5
		self.hp_expo = 1.5
		self.mp_expo = 1.1
		self.armor = 20
		self.magic_resist = 20
		self.armor_base = 20
		self.armor_expo = 1.5
		self.magic_resist_base = 20
		self.magic_resist_expo = 1.5
		
		self.armor_pen = 0
		self.magic_pen = 0
		
		#--- Walk animation variables ---
		
		self.imgs = [""]
		self.img_walk = 0
		self.img_sword = 1
		self.ani_walk = self.ani_setup(3, "images\\hero\\walk\\*.png", self.img_walk)
		self.ani_idle = self.ani_setup(8, "images\\hero\\idle\\*.png", self.img_walk)
		self.ani_up = self.ani_setup(10, "images\\hero\\up.png", self.img_walk)
		self.ani_down = self.ani_setup(10, "images\\hero\\down.png", self.img_walk)
		self.ani_attack = self.ani_setup(10, "images\\hero\\attack\\*.png", self.img_walk)
		
		self.attack_display_cd = 0
		self.attack_display_init = 8
		
		self.sword_pos_idle = 3
		self.sword_pos_walk = 4
		self.sword_pos_air = 5
		
		#--- Other ---
		
		self.want_to_ladder = False
		self.stunned = 0
		self.unstopable = 0
		self.view_range = pygame.Rect(0, 0, dis_width, dis_height)
		self.distance_to_screen = 300
		
		#--- Combat ---
		
		self.combo_init = 30
		self.combo = 0
		self.combo_one_cd = 0
		self.combo_two_cd = 0
		self.combo_three_cd = 0
	
		self.attack_cd = 0
		self.attack_cd_init = self.equips[0].attack_cd
		
		#--- Jumping variables ---
		
		self.jump_power = -13
		self.jump_power_launch = -19
		self.floor_collision = False
		self.jumps = 10000
		self.jumps_init = self.jumps
		self.jump_duration = 0
		self.jump_duration_init = 10
	
		#--- Inventory
	
		self.inventory = [[],[]]
	
	def move(self, room):
		if self.xp_curr >= self.xp_max:
			self.levelup()
			
		self.temp_ladder_bool = self.on_ladder(room.ladders)
			
		if self.changed_dir and self.x == self.display_x:
			self.x += 18
		elif self.changed_dir:
			self.x -= 18
		
		#--- Countdowns ---
		
		if self.combo_one_cd != 0:
			self.combo_one_cd -= 1
		if self.combo_two_cd != 0:
			self.combo_two_cd -= 1
		if self.combo_three_cd != 0:
			self.combo_three_cd -= 1
			
		if self.attack_display_cd != 0:
			self.attack_display_cd -= 1
			
		if self.attack_cd != 0:
			self.attack_cd -= 1
		else:
			for type in room.enemies:
				for enemy in type:
					enemy.has_recieved_dmg = False
			
		if self.stunned > 0: 
			self.friction()
			self.stunned -= 1
		else:
			self.can_move_x = True
			
		if self.unstopable != 0:
			self.unstopable -= 1
		
		if self.jump_duration != 0:
			self.jump_duration -= 1
		
		#--- Replace side, rectangle variables ---
		
		self.rect = (self.x, self.y, self.w, self.h)
		self.sides()
		
		#--- Ladder stuff --- 

		self.attched_on_ladder = False
		
		if self.temp_ladder_bool and self.want_to_ladder:
			self.attched_on_ladder = True
		elif not self.temp_ladder_bool:
			self.attched_on_ladder = False
			self.want_to_ladder = False
		
		if not self.attched_on_ladder:
			self.floor_collision = self.gravity(room.floors)
		
		if self.temp_ladder_bool and self.want_to_ladder:
			self.speed[1] = self.ladder_speed
	
		#--- Jumping ---
		
		if self.floor_collision:
			self.jumps = self.jumps_init
		
		if self.jump_duration > self.jump_duration_init - 8:
			self.speed[1] = self.jump_power
		
	
		#--- Allowing x movement ---
	
		for floor in room.floors:
			if (not (self.collide(self_part = self.side_left, other_part = floor.side_right) and self.speed[0] <= 0)) and (not (self.collide(self_part = self.side_right, other_part = floor.side_left) and self.speed[0] >= 0)):
				pass
			else:
				self.can_move_x = False
				
		#--- Animation ---
		
		if self.combo != 0 and self.attack_display_cd != 0:
			self.imgs[self.img_walk] = pygame.image.load(self.anis[self.ani_attack][2][self.combo - 1])
			self.equips[0].img_number = self.combo - 1
			self.attack_rect = self.equips[0].rect
			
		elif self.speed[0] != 0 and self.speed[1] == 0:
			self.ani_base(self.ani_walk, self.img_walk)
			self.equips[0].img_number = self.sword_pos_walk
			
		elif self.speed[1] == 0:
			self.ani_base(self.ani_idle, self.img_walk)
			self.equips[0].img_number = self.sword_pos_idle
			
		elif self.speed[1] < 0 and not self.attched_on_ladder:
			self.ani_base(self.ani_up, self.img_walk)
			self.equips[0].img_number = self.sword_pos_air
			
		elif not self.attched_on_ladder:
			self.ani_base(self.ani_down, self.img_walk)
			self.equips[0].img_number = self.sword_pos_air
		else:
			self.ani_base(self.ani_idle, self.img_walk)
			self.equips[0].img_number = self.sword_pos_idle

		#--- Attack collision check ---
		
		if self.attack_display_cd > 0:
			for type in room.enemies:
				for enemy in type:
					if self.collide(self_part = self.attack_rect, other_part = enemy):
						if not enemy.has_recieved_dmg and enemy.alive:
							dmg, dead = enemy.recieve_dmg(self, 5, 0)
							enemy.init_display_health(dmg)
							if dead:
								self.xp_curr += enemy.xp_give
							if self.dir == "left":
								enemy.knockback(enemy, -1, (self.walk_speed, -3), 10)
							else:
								enemy.knockback(enemy, 1, (self.walk_speed, -3), 10)
		
		#--- Screen or regular movement check ---
		
		x_move = False
		y_move = False
		move_room_x = False
		move_room_y = False
		
		if self.can_move_x:
			if self.distance_to_screen > self.x and self.speed[0] < 0 and not self.room_location[0] < 0:
				move_room_x = True
			else:
				x_move = True
			if self.x + self.w > dis_width - self.distance_to_screen and self.speed[0] > 0 and not self.room_location[0] > room.w:
				move_room_x = True
			else:
				x_move = True
			
		if self.distance_to_screen > self.y and self.speed[1] < 0 and not self.room_location[1] < 0:
			move_room_y = True
		else:
			y_move = True
		if self.y + self.h > dis_height - self.distance_to_screen and self.speed[1] > 0 and not self.room_location[1] > room.h:
			move_room_y = True
		else:
			y_move = True
				
		#-- Final movement ---
				
		if y_move:
			self.y += self.speed[1]
		if move_room_y:
			room.move_view((0, self.speed[1]))
		
		if x_move:
			self.x += self.speed[0]
			self.display_x += self.speed[0]
		if move_room_x:
			room.move_view((self.speed[0], 0))
		
		self.changed_dir = False
			
		self.room_location[0] += self.speed[0]
		self.room_location[1] += self.speed[1]
		
	def display(self):
		if self.dir == "right":
			gameDisplay.blit(self.imgs[self.img_walk], (self.x, self.y))
		elif self.dir == "left":
			gameDisplay.blit(pygame.transform.flip(self.imgs[self.img_walk], True, False), (self.display_x, self.y))
		for equip in self.equips:
			equip.display(self.display_x, self.y, self.dir)
		
	def on_ladder(self, ladders):
		for ladder in ladders:
			if self.collide(other = ladder):
				return(True)
			else:
				return(False)

	def levelup(self):
		self.level += 1
		self.xp_max = 30 + self.xp_base * (self.level - 1)**self.xp_expo
		self.xp_curr = 0
		self.hp_max = 23 + self.hp_base * (self.level - 1)**self.hp_expo
		self.hp_curr = self.hp_max
		self.mp_max = 11 + self.mp_base * (self.level - 1)**self.mp_expo
		self.mp_curr = self.mp_max
		self.armor = 20 + self.armor_base * (self.level - 1)**self.armor_expo
		self.magic_resist = 20 + self.magic_resist_base * (self.level - 1)**self.magic_resist_expo
	
	def attack(self):
		if self.attack_cd == 0:
			self.attack_cd = self.attack_cd_init
			self.attack_display_cd = self.attack_display_init
			if self.combo_one_cd > 0:
				if self.combo_two_cd > 0:
					self.combo = 3
					self.combo_three_cd = self.combo_init
				else:
					self.combo = 2
					self.combo_two_cd = self.combo_init
			else:
				self.combo = 1
				self.combo_one_cd = self.combo_init

	def enter_portal(self, exit):
		print("Grattis, du gick in i portal på vägg", exit.wall)
				
class Sword():
	def __init__(self, img_path, sizes, handles, attack_cd): 
		self.sizes = sizes
		self.attack_cd = attack_cd
		self.handles = handles
		self.img = glob.glob(img_path)
		self.img.sort()
		self.img_number = 3
		
	def display(self, x, y, dir):
		if dir == "right":
			self.x = x + hands[self.img_number][0] - self.handles[self.img_number][0]
			self.y = y + hands[self.img_number][1] - self.handles[self.img_number][1]
			try:
				gameDisplay.blit(pygame.image.load(self.img[self.img_number]), (self.x, self.y))
			except:
				gameDisplay.blit(pygame.image.load(self.img[3]), (self.x, self.y))
		else:
			self.x = x + attack_img_size[0] - hands[self.img_number][0] - (self.sizes[self.img_number][0] - self.handles[self.img_number][0])
			self.y = y + hands[self.img_number][1] - self.handles[self.img_number][1]
			try:
				gameDisplay.blit(pygame.transform.flip(pygame.image.load(self.img[self.img_number]), True, False), (self.x, self.y))
			except:
				gameDisplay.blit(pygame.transform.flip(pygame.image.load(self.img[3]), True, False), (self.x, self.y))
		self.rect = pygame.Rect(self.x, self.y, self.sizes[self.img_number][0], self.sizes[self.img_number][1])

class Room():
	def __init__(self, w, h, floors, enemies, projectiles, ladders, spikes, hero, exits, chests, entities):
		self.w = w
		self.h = h
		self.enemies = enemies
		self.floors = floors
		self.ladders = ladders
		self.spikes = spikes
		self.projectiles = projectiles
		self.hero = hero
		self.exits = exits
		self.chests = chests
		self.entities = entities
		
	def move_view(self, speed):
		for floor in self.floors:
			floor.x -= speed[0]
			floor.y -= speed[1]
		for ladder in self.ladders:
			ladder.x -= speed[0]
			ladder.y -= speed[1]
		for spike in self.spikes:
			spike.x -= speed[0]
			spike.y -= speed[1]
		for type in self.enemies:
			for enemy in type:
				enemy.x -= speed[0]
				enemy.y -= speed[1]
		for proj in self.projectiles:
			proj.target_pos[0] -= speed[0]
			proj.target_pos[1] -= speed[1]
			proj.rect.x -= speed[0]
			proj.rect.y -= speed[1]
		for exit in self.exits:
			exit.rect.x -= speed[0]
			exit.rect.y -= speed[1]
		for chest in self.chests:
			chest.x -= speed[0]
			chest.y -= speed[1]
		for entity in self.entities:
			entity.x -= speed[0]
			entity.y -= speed[1]
		
		self.hero.x -= speed[0]
		self.hero.y -= speed[1]
		self.hero.display_x -= speed[0]
		
	def create_random(self, level, min_exits = 1):
		self.exits = []  
		self.floors = [] 
		self.squares = []
		self.circles = []
		self.enemies = []
		self.ladders = []
		self.spikes = [] 
		self.chests = []
		
		w_units = random.randint(15,30)
		h_units = random.randint(15,25)
		
		self.w = w_units * units_size 
		self.h = h_units * units_size
		
		used_walls = []
		created_exits = 0
		
		#--- Create exits ---
		
		exit_count = random.randint(4,4)#random.randint(min_exits, 4)
		
		while created_exits < exit_count:
			wall = random.randint(1,4)
			if wall not in used_walls:
				if wall == 1:
					self.exits.append(Exit(random.randint(1, 4) * units_size, random.randint(2, h_units - 4) * units_size, self.exits, wall))				
				elif wall == 2:
					self.exits.append(Exit(random.randint(1, w_units - 2) * units_size, random.randint(2, 5) * units_size, self.exits, wall))
				elif wall == 3:
					self.exits.append(Exit(self.w - random.randint(2, 5) * units_size, random.randint(2, h_units - 5) * units_size, self.exits, wall))
				elif wall == 4:
					self.exits.append(Exit(random.randint(2, w_units - 2) * units_size, self.h - random.randint(4, 6) * units_size, self.exits, wall))
				used_walls.append(wall)
				created_exits += 1
				
		self.floors.append(Floor(0, self.h - units_size, self.w, 25))
		
		for exit in self.exits:
			self.floors.append(exit.floor)
			length = random.randint(2, 8)
			if abs(exit.rect.x - self.w) < exit.rect.x:
				max_len = abs(exit.rect.x - self.w)/units_size
				if length > max_len:
					length = max_len
				self.floors.append(Floor(exit.rect.x - length * units_size, exit.rect.y + exit.rect.h, length * units_size, 25))
			else:
				max_len = (exit.rect.x + exit.rect.w)/units_size
				if length > max_len:
					length = max_len
				self.floors.append(Floor(exit.rect.x + exit.rect.w, exit.rect.y + exit.rect.h, length * units_size, 25))
				
		lowest_exit = self.get_closest_feature((0, self.floors[0].y), self.exits, False, True)
		self.exits[lowest_exit[0]].color = blue
		print(lowest_exit)
		
		self.enemies.append(self.squares)
		self.enemies.append(self.circles)
		
	def create_path(self, point1, point2):
		pass
		
	def get_closest_feature(self, point, feats, x, y):
		dist = [0,0,0,0]
		for feat in feats:
			if x:
				x_dist = abs(point[0] - feat.x)
				x_diff = abs(x_dist - dist[1])
			if y:
				y_dist = abs(point[1] - feat.y)
				y_diff = abs(y_dist - dist[2])
				
			if x and y and (x_diff + y_diff < dist[3] or dist[3] == 0):
				dist = [feats.index(feat), x_diff, y_diff, x_diff + y_diff]
			elif x and (x_diff < dist[1] or dist[1] == 0):
				dist = [feats.index(feat), x_diff,0,0]
			elif y and (y_diff < dist[2] or dist[2] == 0):
				dist = [feats.index(feat),0, y_diff,0]
		return(dist)

class Exit(Physics):
	def __init__(self, x, y, exits, wall):
		self.x = x
		self.y = y
		self.exits = exits
		self.wall = wall
		self.rect = pygame.Rect(self.x, self.y, units_size/2, units_size)
		self.x, self.y = self.check_exit(self.rect)
		self.floor = Floor(self.rect.center[0] - units_size, self.rect.y + self.rect.h, 2 * units_size, 25)
		self.color = purple

	def check_exit(self, rect):
		can_make_exit = 0
		
		while True:
			can_make_exit = 0
			if self.exits != []:
				for exit in self.exits:
					if self != exit:
						if self.collide(self_part = rect, other_part = exit.rect):
							can_make_exit += 1
			else:
				return(rect.x, rect.y)
			
			if can_make_exit == 0:
				return(rect.x, rect.y)
			else:
				return(self.check_exit(pygame.Rect(rect.x + units_size, rect.y + units_size, units_size/2, units_size)))
			
	def display(self):
		pygame.draw.rect(gameDisplay, self.color, self.rect)

class Chest(Physics):
	def __init__(self, x, floor):
		self.w = 75
		self.h = 50
		if floor.x < x < floor.x + floor.w or floor.x < x + self.w < floor.x + floor.w:
			self.x = x
		else:
			self.x = floor.x + (floor.w - self.w)/2
		self.y = floor.y - self.h
		self.img = pygame.image.load("images\\environment\\generic\\chest.png")
	
	def display(self):
		gameDisplay.blit(self.img, (self.x, self.y))
		
	def open(self):
		print("Opening chest...")
		
class NPC():
	def __inti__(self, floor):
		self.floor = floor
		self.img = pygame.image.load("images\\NPC\\test.png")
		
class Floor(Physics):
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.sides()
	
	def display(self, hero):
		pygame.draw.rect(gameDisplay, gray, (self.x, self.y, self.w, self.h))
		
	def re_pos(self):
		self.sides()
		self.side_top = pygame.Rect((self.x, self.y - 1, self.w, 10))
		
class Prjoectile(Physics):
	def __init__(self, img, target_pos, center_pos, speed, dmg, dmg_type, pen):
		
		self.img = img
		self.target_pos = [target_pos[0], target_pos[1]]
		self.center_pos = center_pos
		self.target_speed = speed
		self.dmg = dmg
		self.dmg_type = dmg_type
		self.armor_pen = pen
		self.magic_pen = pen
		self.rect = self.img.get_rect()
		self.rect.center = center_pos
		self.alive = True
		self.length = [self.target_pos[0] - self.center_pos[0], self.target_pos[1] - self.center_pos[1]]
		
		if self.length[0] != 0:
			self.angle = math.degrees(math.atan(abs(self.length[1])/abs(self.length[0])))
		else:
			self.angle = 90
		self.proj_angle = angleFix(self.target_pos, self.angle, self.center_pos)
		
		new_rect = pygame.transform.rotate(self.img, -self.proj_angle).get_rect()
		self.rect.w = new_rect.w
		self.rect.h = new_rect.h

		self.proj_noChase = False
		
		self.speed = [0,0]
		
	def move(self, floors, hero):
		
		for floor in floors:
			if self.collide(self_part = self.rect, other_part = floor):
				self.alive = False
		if self.collide(self_part = self.rect, other_part = hero):
			hero.recieve_dmg(self, self.dmg, self.dmg_type)
			self.alive = False
		
		if self.length[0] != 0:
			self.angle = math.degrees(math.atan(abs(self.length[1])/abs(self.length[0])))
		else:
			self.angle = 90
		
		self.yinx = math.tan(math.radians(self.angle))
		self.multi = self.target_speed/(self.yinx + 1)
		
		if not (abs(self.length[0]) < 20 and abs(self.length[1]) < 20):
			self.speed = [self.multi * negative(self.length[0]), self.multi * self.yinx * negative(self.length[1])]
			self.length = (self.target_pos[0] - self.rect.center[0], self.target_pos[1] - self.rect.center[1])

		self.rect.center = self.rect.center[0] + self.speed[0], self.rect.center[1] + self.speed[1]
		
	def display(self, hero):
		if self.collide(self_part = self.rect, other_part = hero.view_range):
			gameDisplay.blit(pygame.transform.rotate(self.img, -self.proj_angle), (self.rect.x, self.rect.y))
		
class Ladder(Physics):
	def __init__(self, floor1, floor2, x):
		#--- Base variables ---
		
		self.floors = (floor1, floor2)
		if floor1.y < floor2.y:
			self.floor_upper = floor1
			self.floor_lower = floor2
		else:
			self.floor_upper = floor2
			self.floor_lower = floor1

		if floor1.x < x < floor1.x + floor1.w and floor2.x < x < floor2.x + floor2.w:
			self.x = x
		else:
			print("Ladder error: Floors not over each other")
			
		self.y = self.floor_upper.y - 1
		self.h = self.floor_lower.y - self.floor_upper.y + 1
		self.w = 55
		
	def display(self, hero):
		if self.collide(other = hero.view_range):
			
			#-- Recalculate location ---
			
			self.bar_left = pygame.Rect(self.x, self.y + 1, 10, self.h)
			self.bar_right = pygame.Rect(self.x + self.w, self.y + 1, 10, self.h)
			self.steps = []
			tempVar = 0
			new_y = self.y + self.h - 20
			while new_y > self.y + 50:
				new_y = self.y + self.h - 20 - 50 * tempVar
				tempVar += 1
				self.steps.append((self.x, new_y, self.w, 5))
			
			#-- Display ---
			
			for step in self.steps:
				pygame.draw.rect(gameDisplay, black, step)
			pygame.draw.rect(gameDisplay, black, self.bar_left)
			pygame.draw.rect(gameDisplay, black, self.bar_right)
		
class Spike(Physics):
	def __init__(self, floor, length, x):
		self.x = x
		self.y = floor.y
		self.floor = floor
		self.length = length
		self.list = []
		self.width = 17
		self.w = 17 * length
		self.h = 30
		self.img = pygame.image.load("spikes.png")
		
		for i in range(length):
			self.list.append(pygame.Rect(self.x + i * self.width, self.floor.y - self.h + 1, self.width, self.h))
		
	def display(self, hero):
		if self.collide(other = hero.view_range):
			self.list = [] 
			for i in range(self.length):
				self.list.append(pygame.Rect(self.x + i * self.width, self.floor.y - self.h + 1, self.width, self.h))
			for rect in self.list:
				gameDisplay.blit(self.img, (rect.x, rect.y))
	
class Enemy(Physics, Combat):
	def init_display_health(self, lost):
		self.health_display = self.health_display_init
		self.hp_part = int(50*(self.hp_curr/self.hp_max))
		self.lost_part = int(50 * (lost/self.hp_max))
		w = 50
		h = 10
		x = self.x + self.w/2 - w/2
		y = self.y - 30

		outer_rect = pygame.Rect(x,y,w,h)
		inner_rect = pygame.Rect(x,y,self.hp_part,h)
		yellow_part = pygame.Rect(x + self.hp_part, y, self.lost_part, h)
	
		pygame.draw.rect(gameDisplay, black, outer_rect, 2)
		pygame.draw.rect(gameDisplay, red, inner_rect)
		pygame.draw.rect(gameDisplay, yellow, yellow_part)
		
	def display_health(self):
		if self.alive:
			w = 50
			h = 10
			x = self.x + self.w/2 - w/2
			y = self.y - 30

			outer_rect = pygame.Rect(x,y,w,h)
			inner_rect = pygame.Rect(x,y,self.hp_part,h)
			yellow_part = pygame.Rect(x + self.hp_part, y, self.lost_part * (self.health_display/(self.health_display_init)), h)
		
			pygame.draw.rect(gameDisplay, black, outer_rect, 2)
			pygame.draw.rect(gameDisplay, red, inner_rect)
			pygame.draw.rect(gameDisplay, yellow, yellow_part)
		
	def base_vars(self):
		self.health_display_init = 60
		self.health_display = 0
		self.grav_force = 2
		self.grav_max = 20
		self.friction_force = 0.4
		
		self.dir_cd = random.randint(30, 100)
		self.speed = [0,0]
		
		self.stunned = 0
		self.unstopable = 0
		self.has_recieved_dmg = False
		self.alive = True
		
		self.respawn_cd_init = 100
		self.respawn_cd = self.respawn_cd_init
		self.dead_displaytime = 20

	def display_dead(self):
		self.s = pygame.image.load("images\\enemy\\dead.png")
		self.s = self.s.convert()
		self.s.set_alpha(200 * ((self.respawn_cd - self.respawn_cd_init + self.dead_displaytime)/self.dead_displaytime))	
		gameDisplay.blit(self.s, (self.x, self.y))

	def respawn(self):
		self.speed = [0,0]
		self.alive = True
		self.respawn_cd = self.respawn_cd_init
		self.hp_curr = self.hp_max
		self.health_display = 0
		
	def drop_gold(self):
		pass
		
class Attacking_object():
	def charge_init(self, dist, speed, dir, whindup):
		self.charge_dur = dist/speed
		self.charge_whindup = whindup
		self.charge_speed = speed * dir
		self.stunned = self.charge_dur
		self.charge_has_dmg = False
		self.att_cd = self.att_cd_init
		
	def charge(self, floor, hero, dmg, dmg_type):
		if self.charge_whindup == 0:
			if self.charge_dur != 0 and self.stunned == 0:
				self.charge_dur -= 1
				self.unstopable = 1
				self.speed[0] = self.charge_speed
				if not self.on_floor(floor):
					self.speed[0] = 0
				if self.collide(other = hero):
					self.unstopable = 0
					hero.knockback(hero, negative(self.speed[0]), (hero.walk_speed, -15), 20)
					hero.knockback(self, -negative(self.speed[0]), (hero.walk_speed, -5), 20)
					self.charge_dur = 0
					if not self.charge_has_dmg:
						hero.recieve_dmg(self, dmg, dmg_type)
						self.charge_has_dmg = True
		else:
			self.charge_whindup -= 1
			self.speed[0] = 0

class Square(Enemy, Movable_object, Animation, Attacking_object):
	def __init__(self, floor, type, level):
		
		self.base_vars()

		self.id = 1
		self.type = type
		self.level = level
		self.xp_give = 3
		
		self.dir = -1
		self.walk_speed = 2
		
		if self.type == "normal":
			self.dmg = 1 + self.level * 0.5
			self.hp_curr = 10 + self.level * 1.5
			self.att_cd_max = 30
			self.att_cd = self.att_cd_max
			self.ability = ""
			self.w = 40
			self.h = 40
			self.armor = 20 + self.level * 2
			self.magic_resist = 20 + self.level * 2
		elif self.type == "epic":
			self.dmg = 2 + self.level * 1
			self.hp_curr = 100 + self.level * 15
			self.att_cd_max = 25
			self.att_cd = self.att_cd_max
			self.ability = "stun"
			self.w = 80
			self.h = 80
			self.armor = 20 + self.level * 2
			self.magic_resist = 20 + self.level * 2
			
		self.hp_max = self.hp_curr
		self.armor_pen = 0
		
		self.x = floor.x + (floor.w - self.w)/2 
		self.y = floor.y - self.h
		self.floor = floor
		self.imgs = [""]
		self.sides()
		
		self.img_main = 0
		self.ani_movment = self.ani_setup(10, "images\\enemy\square\walk*.png", self.img_main)
		self.ani_idle = self.ani_setup(10, "images\\enemy\square\idle*.png", self.img_main)
		
		self.attack_range = pygame.Rect(self.x, self.y, 200, self.h)
		self.attack_range.center = pygame.Rect(self.x, self.y, self.w, self.h).center
		
		self.detection_box = pygame.Rect(self.floor.x, self.floor.y, 500, 200)
		self.detection_box.center = pygame.Rect(self.x, self.y, self.w, self.h).center
		
		self.charge_dur = 0
		self.att_cd_init = 30
		self.att_cd = 0
		
		self.idle = False
		self.idle_cd_inti = 70
		self.idle_cd = 0

	def move(self, hero):
		if self.hp_curr <= 0:
			self.alive = False
			if self.respawn_cd == self.respawn_cd_init - 1:
				self.drop()
		if self.alive:
			
			self.sides()
			self.detection_box.center = pygame.Rect(self.x, self.y, self.w, self.h).center
			self.attack_range.center = pygame.Rect(self.x, self.y, self.w, self.h).center
			self.detect_hero = hero.collide(other = self.detection_box)
			self.idle_prob = random.randint(1, 3)
			
			#--- Idle ---
						
			if self.idle_prob == 1 and self.idle_cd == 0:
				self.idle = True
				self.idle_cd = self.idle_cd_inti
			elif self.idle_cd == 0:
				self.idle = False
				self.idle_cd = self.idle_cd_inti
			
			if self.detect_hero:
				self.idle = False
			
			#--- Countdowns ---
			
			if self.stunned > 0:
				self.stunned -= 1
				self.friction()
				
			if self.unstopable != 0:
				self.unstopable -= 1
			
			if self.att_cd > 0 and self.charge_dur == 0:
				self.att_cd -= 1
			
			if self.idle_cd > 0:
				self.idle_cd -= 1
				
			if self.health_display != 0:
				self.health_display -= 1
				self.display_health()
				
			#--- AI ---
			
			if self.stunned == 0:
				if self.detect_hero and self.charge_dur == 0:
					self.dir = negative(hero.x - self.x)
					if not self.on_floor(self.floor):
						if abs(self.x - self.floor.x) < abs(self.x - (self.floor.x + self.floor.w)):
							self.dir = 1
						else:
							self.dir = -1
					self.speed[0] = self.walk_speed * self.dir
					if hero.collide(other = self.attack_range) and self.att_cd == 0 and self.stunned == 0:
						self.attack(hero)
				elif self.charge_dur == 0 and not self.idle:
					self.random_floor_movment(hero, self.floor)
				elif not self.idle:
					self.charge(self.floor, hero, self.dmg, 0)
				else:
					self.speed[0] = 0
			
			#--- Animation ---
			
			if self.speed[0] != 0:
				self.ani_base(self.ani_movment, self.img_main)
			else:
				self.ani_base(self.ani_idle, self.img_main)
			
			#--- Final movement ---	
			
			new_dir = self.stay_on_floor(self.floor)
			if new_dir != None:
				self.dir = new_dir
			
			self.gravity([self.floor])
			
			self.y += self.speed[1]
			self.x += self.speed[0]

		else:
			self.respawn_cd -= 1
			if self.respawn_cd == 0:
				self.respawn()

	def display(self, hero):
		if self.collide(other = hero.view_range) and self.alive:
			gameDisplay.blit(self.imgs[0], (self.x, self.y))
		elif not self.alive and self.respawn_cd >= self.respawn_cd_init - self.dead_displaytime:
			self.display_dead()

	def attack(self, hero):
		if self.att_cd == 0:
			self.charge_init(100, 10, self.dir, 10)

	def knockback(self, target, dir, speed, stun):
		if target.unstopable == 0:
			target.speed[0] = speed[0] * dir
			target.speed[1] = speed[1]
			if not self.on_floor(self.floor):
				self.speed[0] = 0
			target.stunned = stun

	def drop(self):
		self.drop_gold()
			
class Circle(Enemy, Animation):
	def __init__(self, center, type, level):
		
		self.level = level
		self.type = type
		self.center = center
		self.xp_give = 5
		self.id = 2
		
		self.base_vars()

		if self.type == "normal":
			self.dmg = 1 + self.level * 0.5
			self.hp_curr = 10 + self.level * 1.5
			self.att_cd_max = 60
			self.att_cd = 0
			self.ability = ""
			self.w = 43
			self.h = 43
			self.lens_w = 19
			self.lens_h = 19
			self.armor = 15 + self.level * 1.5
			self.magic_resist = 15 + self.level * 1.5
		elif self.type == "epic":
			self.dmg = 2 + self.level * 1
			self.hp_curr = 100 + self.level * 15
			self.att_cd_max = 25
			self.att_cd = self.att_cd_max
			self.ability = "3-shot"
			self.w = 86
			self.h = 86
			self.lens_w = 38
			self.lens_h = 38
			self.armor = 15 + self.level * 1.5
			self.magic_resist = 15 + self.level * 1.5
			
		self.armor_pen = 0
			
		self.hp_max = self.hp_curr
		
		# --- Animation stuff ---
		
		self.img_blink = 0
		self.img_idle = 1
		self.img_back = 2
		self.imgs = ["","",""]
		self.proj_img = pygame.image.load("images\\enemy\circle\proj.png")
		self.ani_back = self.ani_setup(1, "images\\enemy\circle\\back.png", self.img_back)
		self.ani_blink = self.ani_setup(2, "images\\enemy\circle\\blink*.png", self.img_blink)
		self.ani_idle = self.ani_setup(10, "images\\enemy\circle\idle*.png", self.img_idle)
		
		# --- Rect vars ---
		
		self.x = 0
		self.y = 0

		self.proj_speed = 7
		self.proj_rect = pygame.Rect(0,0,21,13)
		
		self.rect = pygame.Rect((self.x, self.y, self.w, self.h))
		self.rect.center = self.center
		self.x = self.rect.x
		self.y = self.rect.y
		self.len_rect = pygame.Rect((self.x, self.y, self.lens_w, self.lens_h))
		self.len_rect.center = self.center
		
		self.sides()
		
		self.att_range = pygame.Rect((0, 0, 700, 300))
		self.att_range.center = self.center

		self.pos = ()

		self.blink_durr = 0
		self.blink_durr_init = 10
		
	def AI(self, hero, room):
		if self.hp_curr <= 0:
			self.alive = False
		if self.alive:
			self.detect_hero = hero.collide(other = self.att_range)
			self.center = pygame.Rect(self.x, self.y, self.w, self.h).center
			self.att_range.center = self.center
			self.len_rect.center = self.center
			
			if self.unstopable != 0:
				self.unstopable -= 1
			
			if self.att_cd != 0:
				self.att_cd -= 1
				
			if self.blink_durr != 0:
				self.blink_durr -= 1
			
			if self.health_display != 0:
				self.health_display -= 1
				self.display_health()
			
			# --- Attacking AI ---
			
			if self.detect_hero and (self.att_cd == 0 or self.pos == ()):
				self.pos = (hero.x + hero.w/2, hero.y + hero.h/2)
			elif not self.detect_hero:
				self.pos = ()
				
			if self.detect_hero and self.att_cd == 0:
				self.attack(room)
				self.att_cd = self.att_cd_max

			#--- Looking at player ---

			if self.detect_hero:
				self.pos2 = (hero.x + hero.w/2, hero.y + hero.h/2)
				self.length = [self.pos2[0] - self.center[0], self.pos2[1] - self.center[1]]
				if self.length[0] != 0:
					self.angle = math.degrees(math.atan(abs(self.length[1])/abs(self.length[0])))
				else:
					self.angle = 90
				r = (self.w - self.len_rect.w)/2
				l1 = math.cos(math.radians(self.angle)) * r
				l2 = math.sin(math.radians(self.angle)) * r
				self.len_rect.center = (self.center[0] + l1 * negative(self.length[0]), self.center[1] + l2 * negative(self.length[1]))
			else:
				self.len_rect.center = self.center
				
			#--- Animation stuff ---
				
			if self.detect_hero:
				self.imgs[self.img_idle] = pygame.image.load(self.anis[self.ani_idle][2][0])
				if self.att_cd == self.att_cd_max:
					self.blink_durr = self.blink_durr_init
				if self.blink_durr != 0:
					self.ani_base(self.ani_blink, self.img_blink)
				else:
					self.imgs[self.img_blink] = pygame.image.load(self.anis[self.ani_blink][2][0])
			else:
				self.imgs[self.img_blink] = pygame.image.load(self.anis[self.ani_blink][2][0])
				self.ani_base(self.ani_idle, self.img_idle)
		else:
			self.respawn_cd -= 1
			if self.respawn_cd == 0:
				self.respawn()
			
	def attack(self, room):
		room.projectiles.append(Prjoectile(self.proj_img, self.pos, self.center, self.proj_speed, 5, 0, 0)) #hardcode 5 är skadan av attacken 0 är typen och den andra nollan är pen
		
	def display(self, hero):
		if self.collide(other = hero.view_range) and self.alive:
			gameDisplay.blit(self.imgs[self.img_back], (self.x , self.y))
			gameDisplay.blit(self.imgs[self.img_idle], (self.len_rect.x, self.len_rect.y))
			if self.blink_durr != 0:
				gameDisplay.blit(self.imgs[self.img_blink], (self.x, self.y))
		elif not self.alive and self.respawn_cd >= self.respawn_cd_init - self.dead_displaytime:
			self.display_dead()

class GUI():
	def __init__(self, hero):
		self.hero = hero
		self.bar_health = pygame.Rect(5,10,103,15)
		self.bar_mana = pygame.Rect(5,30,103,15)
		self.bar_xp = pygame.Rect(5,50,103,15)
		
	def displayGUI(self):
		pygame.draw.rect(gameDisplay, black, self.bar_health, 2)
		pygame.draw.rect(gameDisplay, black, self.bar_mana, 2)
		pygame.draw.rect(gameDisplay, black, self.bar_xp, 2)
		message_display(str(self.hero.level), gold, 80, center = False, x = 114, y = 0)
		self.mp_part = int(100 * self.hero.mp_curr/self.hero.mp_max)
		self.hp_part = int(100 * self.hero.hp_curr/self.hero.hp_max)
		self.xp_part = int(100 * self.hero.xp_curr/self.hero.xp_max)
		
		pygame.draw.rect(gameDisplay, blue, (self.bar_mana.x + 2, self.bar_mana.y + 2, self.mp_part, self.bar_mana.h - 3))
		pygame.draw.rect(gameDisplay, red, (self.bar_health.x + 2, self.bar_health.y + 2, self.hp_part, self.bar_health.h - 3))
		pygame.draw.rect(gameDisplay, yellow, (self.bar_xp.x + 2, self.bar_xp.y + 2, self.xp_part, self.bar_xp.h - 3))
	
		message_display(str(int(self.hero.hp_curr)) + " / " + str(int(self.hero.hp_max)), black, 12, center = False, x = 7, y = 12)
		message_display(str(int(self.hero.mp_curr)) + " / " + str(int(self.hero.mp_max)), black, 12, center = False, x = 7, y = 32)
		message_display(str(int(self.hero.xp_curr)) + " / " + str(int(self.hero.xp_max)), black, 12, center = False, x = 7, y = 52)
		
		message_display(str(int(self.hero.room_location[0])) + " " + str(int(self.hero.room_location[1])), black, 25, 0.05, True)

def toggle_dir(dir):
	if dir == -1:
		return(1)
	else:
		return(-1)
		
def negative(x):
	if x >= 0:
		return(1)
	else:
		return(-1)

def angleFix(pos, angle, centerPos):
	if pos[0] > centerPos[0] and pos[1] < centerPos[1]:
		angle = abs(90 - angle) + 90
	elif pos[0] > centerPos[0] and pos[1] > centerPos[1]:
		angle += 180
	elif pos[0] < centerPos[0] and pos[1] > centerPos[1]:
		angle = abs(90 - angle) + 270
	return(angle)
		
def button(text, rect_x, rect_y, rect_w, rect_h, func, active_color, disabled_color, text_color = black, text_size = 25):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	
	if rect_x + rect_w > mouse[0] > rect_x and rect_y + rect_h > mouse[1] > rect_y:
		pygame.draw.rect(gameDisplay, active_color, (rect_x, rect_y, rect_w, rect_h))
		if click[0] == 1:
			returnVar = func()
			if returnVar != None:
				return(returnVar)
	else:
		pygame.draw.rect(gameDisplay, disabled_color, (rect_x, rect_y, rect_w, rect_h))
	
	textFont = pygame.font.Font("freesansbold.ttf", text_size)
	TextSurf, TextRect = text_objects(text, textFont, text_color)
	TextRect.center = ((2 * rect_x + rect_w) / 2 ,(2 * rect_y + rect_h) / 2) 
	gameDisplay.blit(TextSurf,TextRect)
	
def text_objects(text, font, color = black):
	textSurface = font.render(text, True, color)
	return(textSurface,textSurface.get_rect())
	
def message_display(text, color, size, height = 0.2, center = True, x = 0, y = 0):	
	largeText = pygame.font.Font("freesansbold.ttf", size)
	TextSurf, TextRect = text_objects(text, largeText, color)
	if center:
		TextRect.center = ((dis_width/2),(dis_height * height))
	else:
		TextRect.x = x
		TextRect.y = y
	gameDisplay.blit(TextSurf,TextRect)
	
	gameDisplay.blit(TextSurf, TextRect)

def game_quit():
	pygame.quit()
	sys.exit()
	
def game_over(mess):
	while True:
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_quit()
		
		gameDisplay.fill(white)
		
		message_display(mess, black, 50, 0.1)
		button("Try again", 100, 650, 125, 50, game_loop, light_green, green)
		button("Quit", dis_width - 125 - 100, 650, 125, 50, game_quit, light_red, red)
		
		pygame.display.update()
		clock.tick(FPS)

def game_loop():
	#test room
	
	floors = []
	ladders = []
	spikes = []
	squares = []
	circles = []
	projectiles = []
	enemies = []
	exits = []
	chests = []
	entities = []
	floors.append(Floor(100, 700, 500, 25))
	floors.append(Floor(200, 200, 300, 25))
	floors.append(Floor(600, 700, 400, 25))
	floors.append(Floor(600, 200, 300, 25))
	floors.append(Floor(1500, 700, 100, 25))
	chests.append(Chest(500, floors[0]))
	chests.append(Chest(500, floors[1]))
	ladders.append(Ladder(floors[0], floors[1], 300))
	exits.append(Exit(1500, 1000, exits, 1))	
	exits.append(Exit(1500, 1000, exits, 1))
	squares.append(Square(floors[3], "normal", 1))
	circles.append(Circle((700,500), "normal", 1))
	spikes.append(Spike(floors[0], 6, 200))
	entities.append(Entity(700, 200, 29, 28, pygame.image.load("images\\entity\\coin.png"), 1, 1))
	sword = Sword("images\\hero\\equipments\\swords\\basic\\*.png", [(105,31),(48,42),(107,94),(38,38),(38,38),(38,38)],[(49,8),(5,4),(46,85),(6,31),(6,31),(6,31)], 10)
	equips = [sword]
	hero = BaseHero(0,0,40,87, [0, 0], equips)
	gui = GUI(hero)
	
	enemies.append(squares)
	enemies.append(circles)
	
	room = Room(3000, 2000, floors, enemies, projectiles, ladders, spikes, hero, exits, chests, entities)
	#room.create_random(1)
	
	while True:
		
		gameDisplay.fill(white)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_quit()
		
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					hero.speed[0] = -hero.walk_speed
					if hero.dir == "right":
						hero.changed_dir = True
					hero.dir = "left"
				if event.key == pygame.K_RIGHT:
					hero.speed[0] = hero.walk_speed
					if hero.dir == "left":
						hero.changed_dir = True
					hero.dir = "right"
				if event.key == pygame.K_SPACE:
					hero.want_to_ladder = False
					if hero.jumps > 0:
						hero.jump_duration = hero.jump_duration_init
						hero.jumps -= 1
				if event.key == pygame.K_UP:
					for exit in room.exits:
						if hero.collide(other = exit.rect):
							hero.enter_portal(exit)
					for chest in chests:
						if chest.collide(other = hero):
							chest.open()
							
					hero.ladder_speed = -8
					hero.want_to_ladder = True
				if event.key == pygame.K_DOWN:
					hero.ladder_speed = 8
					hero.want_to_ladder = True
				if event.key == pygame.K_q:
					game_quit()	
				if event.key == pygame.K_l:
					hero.levelup()
				if event.key == pygame.K_a:
					hero.attack()
				if event.key == pygame.K_r:
					game_loop()
			
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT and hero.speed[0] < 0:
					hero.speed[0] = 0
				if event.key == pygame.K_RIGHT and hero.speed[0] > 0:
					hero.speed[0] = 0
				if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					hero.ladder_speed = 0
				if event.key == pygame.K_SPACE:
					hero.jump_duration = 0

		hero.move(room)
		
		for floor in room.floors:
			floor.re_pos()

		for square in room.enemies[0]:
			square.move(hero)
			square.display(hero)
		
		for circle in room.enemies[1]:
			circle.AI(hero, room)
			circle.display(hero)
		
		for proj in room.projectiles:
			proj.move(room.floors, hero)
			proj.display(hero)
			if not proj.alive:
				room.projectiles.pop(room.projectiles.index(proj))
		
		for floor in room.floors:
			floor.display(hero)
		
		for entity in room.entities:
			entity.move(room.floors)
			entity.display()
			
		for exit in room.exits:
			exit.display()
			
		for chest in room.chests:
			chest.display()
		
		for ladder in room.ladders:
			ladder.display(hero)
		
		for spike in room.spikes:
			spike.display(hero)
			for obj in spike.list:
				if hero.collide(other = obj):
					game_over("You got impaled  by spikes")
					break
		
		if hero.y > dis_height:
			game_over("You fell out of the world")
			break
		if hero.hp_curr <= 0:
			game_over("You got slain")
			break
		
		hero.display()
		gui.displayGUI()
		pygame.display.update()
		clock.tick(FPS)
		
game_loop()