import math
import pygame
from car import Car

pygame.display.set_caption("Track navigator")
clock = pygame.time.Clock()

TRACK = pygame.image.load("assets/track.png")
TRACK_BORDER = pygame.image.load("assets/track-hitbox.png")
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

WIN_SIZE = (1280, 720)
WIN = pygame.display.set_mode(WIN_SIZE, flags=pygame.SCALED, vsync=1)
FPS = 30


car = Car()

def draw(win, car):
    win.blit(TRACK, (0, 0))
    win.blit(TRACK_BORDER, (0, 0))

    car.draw(win)

def move(car, keys):
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

def unstuck(car, keys):
    if keys[pygame.K_w]:
        car.vel = -2
    elif keys[pygame.K_s]:
        car.vel = 2

running = True
while running:
    clock.tick(FPS)     # clock.tick_busy_loop(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
    draw(WIN, car)
    move(car, keys)

    if car.collide(TRACK_BORDER_MASK) != None:
        pygame.draw.circle(WIN, (255, 0, 0), car.collide(TRACK_BORDER_MASK), 4)
        if car.vel == 0:    # if stuck, force the car the other way
            unstuck(car, keys)
        else:
            car.hit_wall()
    
    
    line_surface = pygame.Surface((WIN_SIZE[0]-5, WIN_SIZE[1]-5), pygame.SRCALPHA)
    end_x = car.x + math.cos(math.radians(car.angle)) * WIN_SIZE[0]
    end_y = car.y - math.sin(math.radians(car.angle)) * WIN_SIZE[1]
    pygame.draw.line(line_surface, (0,0,255), (car.x + car.img.get_width() / 2, car.y + car.img.get_height() / 2), (end_x, end_y), 3)
    line_mask = pygame.mask.from_surface(line_surface)
    if line_mask.overlap(TRACK_BORDER_MASK, (0,0)):
        poc = line_mask.overlap(TRACK_BORDER_MASK, (0,0))
        pygame.draw.line(line_surface, (0,255,0), (car.x + car.img.get_width() / 2, car.y + car.img.get_height() / 2), poc, 4)
        WIN.blit(line_surface, (0, 0))
        print("Collision detected on " + str(poc))


    pygame.display.update()


pygame.quit()
