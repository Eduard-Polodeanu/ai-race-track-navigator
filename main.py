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



def draw(win):
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


def move_AI(car, predictions, threshold=0.5):
    moving = False

    if predictions[0, 2] > threshold:
        if not predictions[0, 1]:
            car.rotate(left=True)
        else:
            car.rotate(right=True)
    if predictions[0, 3] > threshold:
        if not predictions[0, 1]:
            car.rotate(right=True)
        else:
            car.rotate(left=True)

    if predictions[0, 0] > threshold:
        moving = True
        car.move_forward()
    if predictions[0, 1] > threshold:
        moving = True
        car.move_backward()

    if not moving:
        car.reduce_speed()



car = Car()
step = step2 = step3 = 5
running = True
while running:
    clock.tick(FPS)     # clock.tick_busy_loop(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
    draw(WIN)
    move_player(car, keys)

    if car.collide(TRACK_BORDER_MASK) != None:
        car.hit_wall()
    else:

        ray_end_frontside = (car.x + math.cos(math.radians(car.angle)) * step, car.y - math.sin(math.radians(car.angle)) * step)
        ray_end_leftside = (car.x + math.cos(math.radians(car.angle + 90)) * step2, car.y - math.sin(math.radians(car.angle + 90)) * step2)
        ray_end_rightside = (car.x + math.cos(math.radians(car.angle - 90)) * step3, car.y - math.sin(math.radians(car.angle - 90)) * step3)

        rays_surface = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
        rays_surface2 = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
        rays_surface3 = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
        step = car.draw_rays(WIN, rays_surface, step, ray_end_frontside, TRACK_BORDER_MASK)
        step2 = car.draw_rays(WIN, rays_surface2, step2, ray_end_leftside, TRACK_BORDER_MASK)
        step3 = car.draw_rays(WIN, rays_surface3, step3, ray_end_rightside, TRACK_BORDER_MASK)

        distanceV = [step, step2, step3]
        input_data = np.array(distanceV).reshape(1, 3)
        predictions = car.model.predict(input_data)
        print(predictions)
        print()
    
        move_AI(car, predictions)

    pygame.display.update()


pygame.quit()
