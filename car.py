import pygame
import math
import tensorflow as tf
from utils import blit_rotate_center, calculate_distance, scale_image

CAR = scale_image(pygame.image.load("assets/car.png"), 0.5)
CAR_MASK = pygame.mask.from_surface(scale_image(pygame.image.load("assets/car-hitbox.png"), 0.5))
CAR_START_POS = (600, 128)

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
        self.is_dead = False
        self.model = self.setup_model()


    def rotate(self, left=False, right=False):
        self.angle = self.angle % 360
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        if not self.is_dead:
            blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians((self.angle + 270) % 360)
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
        """
        self.is_dead = True
        """

    def setup_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(8, activation='relu', input_dim=3),  # Hidden layer with 8 neurons and ReLU activation
            tf.keras.layers.Dense(4, activation='sigmoid')  # Output layer with 4 neurons and sigmoid activation
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        return model
    
    def draw_rays(self, win, surface, step, end_point, mask):
        ray_start_mid = (self.x + self.img.get_width() / 2, self.y + self.img.get_height() / 2)
        pygame.draw.line(surface, (0,0,255), (ray_start_mid), (end_point), 1)
        line_mask = pygame.mask.from_surface(surface)

        if not line_mask.overlap(mask, (0,0)):     # keep growing the ray until it collides with the wall
            step = step + 20
            distance = step
        elif line_mask.overlap(mask, (0,0)):       # save point of collision and calculate distance to it
            poc = line_mask.overlap(mask, (0,0))
            pygame.draw.line(surface, (0,255,0), (ray_start_mid), poc, 1)
            distance = calculate_distance((self.x, self.y), poc)
            # print("Ray collision detected on " + str(poc) + "; Distance: " + str(distance))

        win.blit(surface, (0, 0))
        return distance
        