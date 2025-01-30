# TITLE: GRID QUEST
# AUTHOR: Rayaan Shaikh
# DATE: January 21, 2025

x = 180
y = 80
import os
os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"

import pgzrun
from pgzhelper import *
import random

TITLE = 'GRID QUEST'
WIDTH = 800
HEIGHT = 800

player = Actor('player_right.gif')
player.x = 400
player.y = 600   # sets the initial position for player

terrain_options = ['grass.png', 'water.png', 'lava.png']

terrain = []
    
# this list contains the animation frame for the player walking
player.images = ['player_right.gif', 'player_walk.gif']
player.fps = 5
player_speed = 5
player_iframes = -60

max_health = 100
health = 100
score = 0
game_start = False
play_button = Actor('play_button')
play_button.x = 400
play_button.y = 600
game_over = False
time_stopped = False

powerup_options = ['heart.png', 'potion.png', 'clock.png', 'wand.png', 'medkit.png']
powerups = []

enemies = []
total_enemies = 0
enemies_left = 1

def random_position():
    """ obtains two random values that fit on the screen and returns a random x and y value"""
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT-400)
    return x, y

def generate_enemies(num):
    """ generates a certain number of enemies according to the agrument for 'num"""
    global total_enemies, enemies_left
    enemies_left = num
    for i in range(num):
        enemy = Actor('wizard.png')
        enemy.pos = random_position()
        enemies.append(enemy)

# this function randomizes each individual tile so that the terrain is different each time
def draw_terrain_tile(x,y):
    '''creates an terrain tile actor based on one of three tile options'''
    global terrain_options
    tile = Actor(terrain_options[random.randint(0,2)])
    terrain.append(tile)
    tile.x = x
    tile.y = y

# draw_terrain_tile is called a total of 16 times of account for every tile on the screen
def generate_terrain():
    '''arranges generated terrain tiles in a grid format and resets variables for the next wave'''
    global time_stopped, player_iframes
    terrain.clear()   # clears the terrain list to avoid incorrect collision with tiles underneath
                      # other tiles
    powerups.clear()
    time_stopped = False
    player_iframes = -60
    terrain_y = 100
    global terrain_options, tile, player
    for i in range(4):
        draw_terrain_tile(100, terrain_y)
        draw_terrain_tile(300, terrain_y)
        draw_terrain_tile(500, terrain_y)
        draw_terrain_tile(700, terrain_y)
        terrain_y += 200
    for tile in terrain:
        if player.colliderect(tile):
            if tile.image == 'lava.png':
                player.pos = random_position()
            else:
                player.x = 400
                player.y = 600
    powerup = Actor(powerup_options[random.randint(0, 4)])
    powerups.append(powerup)
    powerup.x = random.randint(10, WIDTH-10)
    powerup.y = random.randint(10, HEIGHT-10)    # randomizes placement of powerups

generate_enemies(1)
generate_terrain()

def draw():
    global score, game_over, player_iframes, max_health
    screen.clear()
    for tile in terrain:
        tile.draw()
    if not game_start:
        screen.draw.text((TITLE), color = 'white', midtop=(WIDTH//2, 100), fontsize = 150)
        screen.draw.text(('Arrow keys/WASD to move'), midtop=(WIDTH//2, 340), fontsize = 70)
        screen.draw.text(('Spacebar to attack'), midtop=(WIDTH//2, 400), fontsize = 70)
        play_button.draw()
    else:
        for powerup in powerups:
            powerup.draw()
        # generates all enemies in the 'enemies' list
        for enemy in enemies:
            enemy.draw()
        player.draw()
        healthbar_black = Rect((20, 60), (max_health, 20))
        healthbar = Rect((20, 60), (health, 20))
        
        screen.draw.filled_rect(healthbar_black, (0, 0, 0))
        screen.draw.filled_rect(healthbar, (200, 0, 0))
        screen.draw.text(str(score), color = 'white', midtop=(WIDTH//2, 10), fontsize = 70)
    
    if health <= 0:
        game_over = True
        screen.draw.text('GAME OVER', color = 'white', midtop=(WIDTH//2, 200), fontsize = 100)
        screen.draw.text('Press R to restart with upgrades', color = 'white', midtop=(WIDTH//2, 400),
                         fontsize = 60)
        screen.draw.text('Press T to restart without upgrades', color = 'white', midtop=(WIDTH//2, 500),
                         fontsize = 60)
    
def update():
    # controls player movement. The player's animation
    global player_speed, health, game_over, player_iframes, total_enemies, time_stopped, enemies_left, max_health
    if not game_over and game_start:
        if keyboard.UP or keyboard.W:
            player.y -= player_speed
            player.animate()
        if keyboard.DOWN or keyboard.S:
            player.y += player_speed
            player.animate()
        if keyboard.LEFT or keyboard.A:
            player.x -= player_speed
            player.flip_x = True
            player.animate()
        if keyboard.RIGHT or keyboard.D:
            player.x += player_speed
            player.flip_x = False
            player.animate()
            
        player_iframes += 1   # increments invincibility frames sixty times per second

        # TERRAIN INTERACTION
        for tile in terrain:
            if player.colliderect(tile):
                if tile.image == 'water.png':
                    player_speed = 3     # slows down player when walking in water
                elif tile.image == 'lava.png':
                    player_speed = 3     # slows down and damages player when walking in lava
                    if player_iframes >= 0:
                        health -= 4
                        player_iframes = -10
                else:
                    player_speed = 6
                    
        # POWERUP INTERACTION       
        for powerup in powerups:
            if player.colliderect(powerup):
                    if powerup.image == 'heart.png':
                        max_health += 20     # increases max health
                        regen_value = (max_health-health)/2
                        health += regen_value
                    elif powerup.image == 'medkit.png':
                        health = max_health # restores health
                    elif powerup.image == 'potion.png':
                        player_iframes = -300    # makes the player invincible for a short period of time
                    elif powerup.image == 'clock.png':
                        time_stopped = True
                        for tile in terrain:     # turns all lava tiles into water tiles
                            if tile.image == 'lava.png':
                                tile.image = 'water.png'
                    elif powerup.image == 'wand.png':
                        new_terrain = terrain_options[(random.randint(0,2))]
                        for tile in terrain:
                            tile.image = new_terrain
                    powerups.remove(powerup)
                        
        # ENEMY INTERACTION      
        for enemy in enemies:
            if enemy.colliderect(player) and player_iframes > 0 and time_stopped == False:
                health -= 4
                player_iframes = -10     # resets invincibility frames
       
        # this checks if all of the enemies on screen are defeated. If so, it generates more enemies
        # and terrain
        if enemies_left == 0:
            player.x = 400
            player.y = 600
            if total_enemies < 100:
                total_enemies += 1
            generate_terrain()
            generate_enemies(total_enemies)
    
def enemy_movement():
    '''moves the enemies towards the player'''
    global time_stopped
    for enemy in enemies:
        if not time_stopped and game_start:
            direction = enemy.direction_to(player)
            enemy.direction = direction
            enemy.move_in_direction(1)
            if enemy.colliderect(enemy):
                direction = random.randint(-1, 1)  
                enemy.x -= direction        # prevents enemies from colliding with each other
                enemy.y -= direction
clock.schedule_interval(enemy_movement, 0.01)

def on_key_down(key):
    ''' controls key actions for attacking and resetting the game'''
    global score, game_over, health, total_enemies, enemies_left, max_health
    if not game_over:
        sword_struck = True
        if key == keys.SPACE:
            player.image = 'player_sword.gif'
            for enemy in enemies:
                if player.colliderect(enemy):
                    enemies.remove(enemy)    # eliminates enemies when hit with a sword
                    score += 1
                    enemies_left -= 1
    else:
        if key == keys.R:      # resets the game with upgrades
            enemies.clear()
            game_over = False
            total_enemies = 0
            generate_terrain()
            generate_enemies(1)
            player.x = 400
            player.y = 500
            health = max_health
            enemies_left = 1
            score = 0
        elif key == keys.T:    # resets the game without upgrades
            enemies.clear()
            game_over = False
            total_enemies = 0
            generate_terrain()
            generate_enemies(1)
            player.x = 400
            player.y = 500
            health = 100
            max_health = 100
            enemies_left = 1
            score = 0

def on_key_up(key):
    '''sheathes the sword after the player's attack is finished'''
    global sword_struck, game_over, player_iframes
    if not game_over:
        if key == keys.SPACE:
            player.image = 'player_right.gif'
            player_iframes -= 5   # by adding invicibility frames when attacking, the player
                                  # can attack without receiving damage in return if the
                                  # timing is exact
            sword_struck = False
            
def on_mouse_down(pos):
    global game_start
    if play_button.collidepoint(pos):
        game_start = True

pgzrun.go()       # runs the program