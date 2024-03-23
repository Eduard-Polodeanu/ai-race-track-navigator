import pygame
import math
from utils import blit_rotate_center, scale_image

CAR = scale_image(pygame.image.load("assets/car.png"), 0.5)
CAR_MASK = pygame.mask.from_surface(scale_image(pygame.image.load("assets/car-hitbox.png"), 0.5))
CAR_START_POS = (400, 64)

MAX_VELOCITY = 4
ROTATION_VELOCITY = 4
ACCELERATION = 0.1


class Car:
    def __init__(self):
        self.img = CAR
        self.mask = CAR_MASK
        self.x, self.y = CAR_START_POS
        self.angle = 0
        self.vel = 0
        self.max_vel = MAX_VELOCITY
        self.rotation_vel = ROTATION_VELOCITY
        self.acceleration = ACCELERATION

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle + 270)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def collide(self, mask, x=0, y=0):
        offset = (int(self.x - x), int(self.y - y))
        intersection_point = mask.overlap(self.mask, offset)
        return intersection_point
    
    def hit_wall(self):
        if self.vel > 0.1:
            self.vel = -self.vel/2
            self.move()
        else:
            self.vel = -self.vel
            self.move()