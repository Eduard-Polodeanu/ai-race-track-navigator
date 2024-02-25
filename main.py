import pygame
import math


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

# draw the image based on the rotation angle of the car
def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


TRACK = pygame.image.load("assets/track.png")
TRACK_BORDER = pygame.image.load("assets/track-hitbox.png")
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

CAR = scale_image(pygame.image.load("assets/car.png"), 0.5)
CAR_MASK = pygame.mask.from_surface(scale_image(pygame.image.load("assets/car-hitbox.png"), 0.4))

WIN_SIZE = (1280, 720)
WIN = pygame.display.set_mode(WIN_SIZE, flags=pygame.SCALED, vsync=1)

pygame.display.set_caption("Racing Game!")

FPS = 30
START_POS = (400, 64)

MAX_VELOCITY = 4
ROTATION_VELOCITY = 4
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

    def collide(self, mask, x=0, y=0):
        offset = (int(self.x - x), int(self.y - y))
        intersection_point = mask.overlap(CAR_MASK, offset)
        print(intersection_point)
        return intersection_point
    
    def hit_wall(self):
        self.vel = -self.vel/2
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
    clock.tick(FPS) # clock.tick_busy_loop(FPS)

    draw(WIN, images, car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_a]:
        car.rotate(left=True)
    if keys[pygame.K_d]:
        car.rotate(right=True)
    if keys[pygame.K_w]:
        moving = True
        car.move_forward()
    if keys[pygame.K_s]:
        moving = True
        car.move_backward()

    if not moving:
        car.reduce_speed()


    if car.collide(TRACK_BORDER_MASK) != None:
        car.hit_wall()
    

pygame.quit()
