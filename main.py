import pygame
import math


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


TRACK = scale_image(pygame.image.load("assets/track.png"), 1)
TRACK_BORDER = scale_image(pygame.image.load("assets/track-border.png"), 1)

CAR = scale_image(pygame.image.load("assets/car.png"), 0.5)

WIN_SIZE = (1280, 720)
WIN = pygame.display.set_mode(WIN_SIZE)

pygame.display.set_caption("Racing Game!")

FPS = 60
START_POS = (180, 70)

MAX_VELOCITY = 3
ROTATION_VELOCITY = 2.2
ACCELERATION = 0.1


class Car:
    def __init__(self, max_vel, rotation_vel, acceleration):
        self.img = CAR
        self.x, self.y = START_POS
        self.angle = 270
        self.vel = 0
        self.max_vel = max_vel
        self.rotation_vel = rotation_vel
        self.acceleration = acceleration

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
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()


def draw(win, images, car):
    for img, pos in images:
        win.blit(img, pos)

    car.draw(WIN)
    pygame.display.update()


running = True
clock = pygame.time.Clock()
images = [(TRACK, (0, 0)), (TRACK_BORDER, (0, 0))]
car = Car(MAX_VELOCITY, ROTATION_VELOCITY, ACCELERATION)

while running:
    clock.tick(FPS)

    draw(WIN, images, car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        car.rotate(left=True)
    if keys[pygame.K_d]:
        car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        car.move_backward()

    if not moved:
        car.reduce_speed()


pygame.quit()
