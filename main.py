import sys
import time
from math import sin, cos
from random import choice, randint
from typing import List

from Timer import Timer
from settings import *
import random


def drawQuad(
        surface: pygame.Surface,
        color: pygame.Color,
        x1: int,
        y1: int,
        w1: int,
        x2: int,
        y2: int,
        w2: int,
):
    # trapezoidal
    pygame.draw.polygon(surface, color, [(x1 - w1, y1), (x2 - w2, y2),
                                         (x2 + w2, y2), (x1 + w1, y1)])


class Line:

    def __init__(self):
        self.x = self.y = self.z = 0.0  # 3d space position
        self.X = self.Y = self.W = 0.0  # 2d space position
        self.scale = 0.0  # scale
        self.curve = 0.0  # for curvature surface

        self.sprite_x = 0.0  # sprite x position
        self.adj_sprite_y = 0.0  # adjust sprite y position
        self.sprite: pygame.Surface = None
        self.sprite_rect = pygame.Rect = None
        self.sprite_type = None

        self.grass_color: pygame.Color = "black"
        self.rumble_color: pygame.Color = "black"
        self.road_color: pygame.Color = "black"
        self.font = pygame.font.Font("images/joystix.ttf", 50)

        self.timer = Timer(2000)

    def drawSprite(self, draw_surface: pygame.Surface, main_rect, player_image):

        self.timer.update()
        collided = False

        if self.sprite is None:
            return

        w = self.sprite.get_width()
        h = self.sprite.get_height()

        destX = self.X + self.scale * self.sprite_x * SCREEN_WIDTH / 2
        destY = self.Y + 4

        destW = w * self.W / 266  # deformed size for width and height based on view from distance
        destH = h * self.W / 266

        destX += destW * self.sprite_x
        destY += destH * -1

        clipH = destY + destH - self.adj_sprite_y
        if clipH < 0:
            clipH = 0
        if clipH >= destH:
            return

        # avoid scaling up images which causes lag
        if destW > w + 400:
            return

        scaled_sprite = pygame.transform.scale(self.sprite, (destW, destH))
        crop_surface = scaled_sprite.subsurface(0, 0, destW, destH - clipH)

        # draw sprites
        draw_surface.blit(crop_surface, (destX, destY))
        main_hitbox = main_rect.inflate(0, -10)  # shrink to fit with the actual

        if self.sprite_type == "car":

            self.sprite_rect = self.sprite.get_rect()
            self.sprite_rect.topleft = (destX, destY)

            self.hit_box = self.sprite_rect.copy()
            self.hit_box.size = (destW, destH)

            pygame.draw.rect(draw_surface, "red", self.hit_box, 2, 2)

            if self.hit_box.colliderect(main_hitbox):
                print("Yes, collision !! ")
                collided = True
                if not self.timer.active:
                    self.timer.timer_on()

            if self.timer.active:
                text_surf = self.font.render("Collision!!!", "False", "red")
                draw_surface.blit(text_surf, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        draw_surface.blit(player_image, main_rect)
        pygame.draw.rect(draw_surface, "green", main_hitbox, 2, 2)
        if collided:
            return True
        else:
            return False

    def projection(self, camX: int, camY: int, camZ: int):
        self.scale = cam_depth / (self.z - camZ)
        # getting 2D space position and convert to 3D projection

        self.X = (1 + self.scale * (self.x - camX)) * SCREEN_WIDTH / 2
        self.Y = (1 - self.scale * (self.y - camY)) * SCREEN_HEIGHT / 2
        self.W = self.scale * road_width * SCREEN_WIDTH / 2


class Game:

    def __init__(self):

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
        self.last_time = time.time()

        # loading background
        self.bg_image = pygame.image.load("images/img_1.png").convert_alpha()
        self.bg_image = pygame.transform.scale(self.bg_image, (1024, 700))

        self.bg_surf = pygame.Surface(
            (self.bg_image.get_width() * 3, self.bg_image.get_height()))

        self.bg_surf.blit(self.bg_image, (0, 0))
        self.bg_surf.blit(self.bg_image, (self.bg_image.get_width() * 2, 0))  # right
        self.bg_surf.blit(self.bg_image, (-self.bg_image.get_width(), 0))  # left

        self.bg_rect = self.bg_surf.get_rect(topleft=(0, 0))

        # sprites
        self.sprites: list[pygame.Surface] = []
        self.car_sprites: list[pygame.Surface] = []

        for i in range(1, objects_num):
            self.sprites.append(pygame.image.load(f"images/{i}.png").convert_alpha())

        for j in range(0, 8):
            img = pygame.image.load(f"images/car{j}.png")
            if j == 0 or j == 6:
                img = pygame.transform.scale(img, (enemy_car_size, enemy_car_size)).convert_alpha()

            self.car_sprites.append(img)

        self.dt = 0
        self.pos = 0
        self.startPos = 0
        self.player_x = 0
        self.player_y = start_elevation

        self.distanceX_to_track: list[float] = [2.2, 3.5, 4.5, 5.8, 6.2, 8.5, -2.1, -3.3, -4.2, -5.0, -7.0, -9.0]
        self.distanceZ: list[float] = [10, 50, 80, 99, 110, 200, 240, 340, 390, 420, 520, 650]

        self.speed = 0
        self.delta_time = min_speed

        # my car
        img = pygame.image.load("images/player.png").convert_alpha()
        left_img = pygame.image.load("images/player_left.png").convert_alpha()
        right_img = pygame.image.load("images/player_right.png").convert_alpha()

        self.player_image = pygame.transform.scale(img, (240, 120))

        self.left_image = pygame.transform.scale(left_img, (240, 120))
        self.right_image = pygame.transform.scale(right_img, (240, 120))
        self.straight_image = pygame.transform.scale(img, (240, 120))

        self.main_rect = self.player_image.get_rect()

        self.main_rect.x = mid_bottom[0]
        self.main_rect.y = mid_bottom[1]

        self.direction = "straight"
        self.max_cars = 0

        # timers
        self.timers = {

            "on impact": Timer(300),
            "after impact": Timer(500)

        }

    def run(self):

        # create lines
        lines: List[Line] = []  # empty matrix
        cars: List = []  # cars matrix

        # track & road creation
        for i in range(track_length_design):
            line = Line()
            car = Line()
            line.z = i * seg_length + 0.0001  # add this small to avoid divided by zero

            # every 3 or its multiples shall be light color else dark color
            grass_color = light_grass if (i // 3) % 2 else dark_grass
            rumble_color = white_rumble if (i // 3) % 2 else black_rumble
            road_color = light_road if (i // 3) % 2 else dark_road

            line.grass_color = grass_color
            line.rumble_color = rumble_color
            line.road_color = road_color

            lines.append(line)
            cars.append(car)

            ########################################Racking track design
            # creating turning track (right curve)
            if 100 < i < 500:
                line.curve = 0.5

                # push car to the left

            # left curve
            if 800 < i < 1000:
                line.curve = -0.4

                # push car to the right

            # creating up/down track using sin/cos curvature
            if i > 700:
                line.y = sin(i / 30.0) * 1000

            if 1000 > i > 800:
                line.y = cos(i / 40.0) * 1000

            if 1400 < i < 1950:
                line.curve = -0.8

            ########################################

            # drawing sprites at different locations - Buildings & obstacles

            # i % (this is occurrence of objects)
            # line.sprite_x = + (right side), -(left side)
            # line.sprite = self.sprites[n] where n is the object image
            for index in range(1, 10):
                if i % choice(self.distanceZ) == 0:
                    line.sprite_x = choice(self.distanceX_to_track)
                    select_object = randint(0, objects_num - 2)
                    line.sprite = self.sprites[select_object]

            #########################################

            # enemy cars on roads
            # between 1.0 and -1.0
            '''
            if i % 100 == 0:
                index = randint(0, 5)
                line.sprite = self.car_sprites[index]

                line.sprite_x = random.uniform(-3.0, 3.0)
                print(line.sprite_x)
                line.sprite_type = "car"

                # cars.append(car)
            '''
            ########################################
        N = len(lines)

        # elapse of time for each frame        self.dt = time.time() - self.last_time
        self.last_time = time.time()
        self.map_cars_update(lines, self.max_cars)

        while True:

            self.screen.fill("green")

            self.update_timers()

            # parallax background
            if self.speed > 0:
                self.bg_rect.x -= lines[self.startPos].curve * 2
            elif self.speed < 0:
                self.bg_rect.x += lines[self.startPos].curve * 2

            if self.bg_rect.right < SCREEN_WIDTH:
                self.bg_rect.x -= lines[self.startPos].curve * 2
            elif self.bg_rect.left > 0:
                self.bg_rect.x += lines[self.startPos].curve * 2

            self.screen.blit(self.bg_surf, self.bg_rect)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            camH = self.player_y + lines[self.startPos].y  # cam H is the elevation , lines.y is the road y
            max_y = SCREEN_HEIGHT
            x, dx = 0, 0

            self.input(N)

            # draw road
            for n in range(self.startPos, self.startPos + show_num_seg):
                current = lines[n % N]

                # looping from start to finish (repeat itself when n > len(lines)
                current.projection(self.player_x - x, camH, self.pos - (N * seg_length if n >= N else 0))
                x += dx
                dx += current.curve

                current.adj_sprite_y = max_y

                if current.Y >= max_y:
                    continue

                max_y = current.Y

                prev = lines[(n - 1) % N]  # previous lines

                # draw grass
                drawQuad(self.screen, current.grass_color, 0, prev.Y, SCREEN_WIDTH, 0, current.Y, SCREEN_WIDTH)

                # draw rumble
                drawQuad(self.screen, current.rumble_color, prev.X, prev.Y, prev.W * 1.2, current.X, current.Y,
                         current.W * 1.2)

                # draw road
                drawQuad(self.screen, current.road_color, prev.X, prev.Y, prev.W, current.X, current.Y, current.W)

            match self.direction:

                case "left":
                    self.player_image = self.left_image
                case "right":
                    self.player_image = self.right_image
                case "straight":
                    self.player_image = self.straight_image

            # reverse draw the buildings
            for n in range(self.startPos + show_num_seg, self.startPos, -1):
                self.collision = lines[n % N].drawSprite(self.screen, self.main_rect, self.player_image)
                if self.collision:
                    self.timers["on impact"].timer_on()
                    break

            # update the new loop and increase more cars
            if self.pos >= 249800:  # reaching end of round
                print("reset the maps !!!!")

                self.map_cars_update(lines, self.max_cars)
                self.max_cars += 1

            self.clock.tick(min_speed + self.delta_time)

            # print(self.speed)
            # print("delta:", self.delta_time)
            # print("offset_x:",self.player_x)

            pygame.display.update()

    def input(self, N):

        keys = pygame.key.get_pressed()

        # acceleration
        if keys[pygame.K_UP] and not self.timers["on impact"].active:
            self.speed = seg_length

            if self.delta_time <= max_speed:
                self.delta_time += 0.1
            elif self.delta_time > 70:
                self.delta_time = 120

        elif self.timers["on impact"].active and not self.timers["after impact"].active:
            self.speed = - 10 * seg_length if self.delta_time > 70 else - 3 * seg_length
            self.timers["after impact"].timer_on()
            self.delta_time = min_speed
            self.player_x -= 100

        elif self.timers["after impact"].active:

            self.speed = 0

        # deceleration by brakes
        elif keys[pygame.K_DOWN] and self.pos > 0:
            self.delta_time -= 1
            if self.delta_time < min_speed:
                self.delta_time = min_speed
                self.speed = 0

        ## deceleration by friction
        else:

            self.delta_time -= 0.2
            self.speed = seg_length
            if self.delta_time < min_speed:
                self.delta_time = min_speed
                self.speed = 0
            ###################
        self.pos += self.speed

        # direction control
        if keys[pygame.K_LEFT]:
            self.player_x -= 50
            self.direction = "left"


        elif keys[pygame.K_RIGHT]:
            self.player_x += 50
            self.direction = "right"


        else:
            self.direction = "straight"

        # elevation
        if keys[pygame.K_w] and self.player_y < elevation_limit:
            self.player_y += 100

        if keys[pygame.K_s] and self.player_y >= start_elevation:
            self.player_y -= 100

        self.speed_limiter()

        # make sure the position not larger than the overall segment/ the road never ends ...
        while self.pos >= N * seg_length:
            self.pos -= N * seg_length
        while self.pos < 0:
            self.pos += N * seg_length

        self.startPos = self.pos // seg_length

    def speed_limiter(self):

        if self.player_x > 1800 or self.player_x < -1800:
            self.delta_time -= 1
            if self.delta_time <= 10:
                self.delta_time = 10

    def map_cars_update(self, lines, max_cars):
        car_dist = 50 * (10 - max_cars)
        if car_dist <= 0:
            car_dist = 50

        print(car_dist)
        for i, line in enumerate(lines):
            if i % (car_dist - max_cars) == 0:
                index = randint(0, 7)
                line.sprite = self.car_sprites[index]
                line.sprite_x = random.uniform(-3.0, 3.0)
                line.sprite_type = "car"

    def update_timers(self):

        for timer in self.timers.values():
            timer.update()


if __name__ == "__main__":
    game = Game()
    game.run()
