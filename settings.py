import pygame
SCREEN_HEIGHT = 850
SCREEN_WIDTH = 1024

road_width = 2000   # from left to right of screen
seg_length = 100  # from top to bottom
cam_depth = 0.9

track_length_design = 2500   # distance of track that would repeat itself

show_num_seg = 300  # No. of lines projections for the screen
objects_num = 13
cars_num = 1

# colors
dark_grass = pygame.Color(0, 154, 0)
light_grass = pygame.Color(0, 154, 0)
white_rumble = pygame.Color(255, 255, 255)
black_rumble =pygame.Color(0,0,0)
dark_road = pygame.Color(105,105,105)
light_road =pygame.Color (107, 107,107)


# elevation parameters - > flying !
start_elevation=800
elevation_limit=30000

my_car_size=180
enemy_car_size= 64
# rectangle
mid_bottom = (SCREEN_WIDTH//2-my_car_size//2, SCREEN_HEIGHT -140 , my_car_size, my_car_size)

max_speed = 100
min_speed =20
