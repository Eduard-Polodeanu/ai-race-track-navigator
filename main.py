import math
import numpy as np
import pygame
from car import Car

pygame.display.set_caption("Track navigator")
clock = pygame.time.Clock()

TRACK = pygame.image.load("assets/track.png")
TRACK_BORDER = pygame.image.load("assets/track-hitbox.png")
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

WIN_SIZE = (1280, 720)
WIN = pygame.display.set_mode(WIN_SIZE, flags=pygame.SCALED, vsync=1)
FPS = 60


car = Car()
model = car.setup_model()

def draw(win, car):
    win.blit(TRACK, (0, 0))
    win.blit(TRACK_BORDER, (0, 0))

    car.draw(win)

def move_player(car, keys):
    moving = False

    if keys[pygame.K_a]:
        if not keys[pygame.K_s]:
            car.rotate(left=True)
        else:
            car.rotate(right=True)
    if keys[pygame.K_d]:
        if not keys[pygame.K_s]:
            car.rotate(right=True)
        else:
            car.rotate(left=True)
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


def calculate_distance(start_point, end_point):
    cateta1 = abs(end_point[0] - start_point[0])
    cateta2 = abs(end_point[1] - start_point[1])
    distance = int(math.sqrt(cateta1*cateta1 + cateta2*cateta2))
    return distance


def draw_rays(win, surface, step, end_point):
    ray_start_mid = (car.x + car.img.get_width() / 2, car.y + car.img.get_height() / 2)
    pygame.draw.line(surface, (0,0,255), (ray_start_mid), (end_point), 1)
    line_mask = pygame.mask.from_surface(surface)

    if not line_mask.overlap(TRACK_BORDER_MASK, (0,0)):     # keep growing the ray until it collides with the wall
        step = step + 20
        distance = step
    elif line_mask.overlap(TRACK_BORDER_MASK, (0,0)):       # save point of collision and calculate distance to it
        poc = line_mask.overlap(TRACK_BORDER_MASK, (0,0))
        pygame.draw.line(surface, (0,255,0), (ray_start_mid), poc, 1)
        distance = calculate_distance((car.x, car.y), poc)
        # print("Ray collision detected on " + str(poc) + "; Distance: " + str(distance))

    win.blit(surface, (0, 0))
    return distance


def move_AI(car, predictions):
    moving = False

    if predictions[0, 2]:
        if not predictions[0, 1]:
            car.rotate(left=True)
        else:
            car.rotate(right=True)
    if predictions[0, 3]:
        if not predictions[0, 1]:
            car.rotate(right=True)
        else:
            car.rotate(left=True)
    if predictions[0, 0]:
        moving = True
        car.move_forward()
    if predictions[0, 1]:
        moving = True
        car.move_backward()

    if not moving:
        car.reduce_speed()




step = step2 = step3 = 5
running = True
while running:
    clock.tick(FPS)     # clock.tick_busy_loop(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
    draw(WIN, car)
    move_player(car, keys)

    if car.collide(TRACK_BORDER_MASK) != None:
        pygame.draw.circle(WIN, (255, 0, 0), car.collide(TRACK_BORDER_MASK), 4)
        if car.vel == 0:    # if stuck, force the car the other way
            unstuck(car, keys)
        else:
            car.hit_wall()
    

    ray_end_frontside = (car.x + math.cos(math.radians(car.angle)) * step, car.y - math.sin(math.radians(car.angle)) * step)
    ray_end_leftside = (car.x + math.cos(math.radians(car.angle + 90)) * step2, car.y - math.sin(math.radians(car.angle + 90)) * step2)
    ray_end_rightside = (car.x + math.cos(math.radians(car.angle - 90)) * step3, car.y - math.sin(math.radians(car.angle - 90)) * step3)

    rays_surface = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
    rays_surface2 = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
    rays_surface3 = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
    step = draw_rays(WIN, rays_surface, step, ray_end_frontside)
    step2 = draw_rays(WIN, rays_surface2, step2, ray_end_leftside)
    step3 = draw_rays(WIN, rays_surface3, step3, ray_end_rightside)

    distanceV = [step, step2, step3]
    print(distanceV)

    input_data = np.array(distanceV).reshape(1, 3)
    predictions = model.predict(input_data)
    print(predictions)
 
    move_AI(car, predictions)

    pygame.display.update()


pygame.quit()
