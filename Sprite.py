from settings import *


# for any images in the game to display
class Sprite(pygame.sprite.Sprite):

    def __init__(self, pos, image, groups):
        super().__init__(groups)

        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

        self.hit_box=self.rect.copy()

# for any images in the game with animation
class Animated_sprite(Sprite):

    def __init__(self, pos, frames, groups, ani_speed):
        self.frames = frames  # got the animation list
        self.frame_index = 0  # animation index
        super().__init__(pos, self.frames[self.frame_index], groups)
        self.pos = pos
        self.animation_speed = ani_speed


    def animate(self):
        self.frame_index += self.animation_speed
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self):
        self.animate()

# for text image to show in the game
class TextSprite:

    def __init__(self, text, pos, color, font):
        super().__init__()

        self.font =font
        self.text= text
        self.color = color
        self.image = self.font.render(self.text, "False", self.color)
        self.rect = self.image.get_frect(center=pos)

    def update(self, screen):

        screen.blit(self.image, self.rect)

# this class is used for display health bars, progress bars, ...
class Bars_Sprite(pygame.sprite.Sprite):
    # value is the existing parameter, max_value is the limit

    def __init__(self, pos, width, height, max_value, color):

        super().__init__()


        self.max_value= max_value
        self.color = color
        self.width = width
        self.height =height
        self.rect = pygame.Rect(pos[0],pos[1],width,height)

        self.bg_color = "grey"

    def update(self, screen, value):

        pygame.draw.rect(screen,self.bg_color,self.rect,0,3)
        ratio = value/self.max_value
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, ratio* self.width, self.height),
                         0, 3)



