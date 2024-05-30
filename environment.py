import pygame
from car import Car
from utils import calculate_line_endpoints

pygame.init()

pygame.display.set_caption("Track navigator")
clock = pygame.time.Clock()

TRACK = pygame.image.load("assets/track.png")
TRACK_BORDER = pygame.image.load("assets/track-hitbox.png")
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

WIN_SIZE = (1280, 720)
WIN = pygame.display.set_mode(WIN_SIZE, flags=pygame.SCALED, vsync=1)
FPS = 60


def draw(win, surfaces, car):
    win.blit(TRACK, (0, 0))
    win.blit(TRACK_BORDER, (0, 0))

    car.draw(win)
    
    draw_rays(surfaces[0], car.center_pos, front_rays_directions, car.angle, 50)
    draw_rays(surfaces[1], car.center_pos, lateral_rays_directions, car.angle, 35) 
    win.blit(surface_front_rays, (0,0))
    win.blit(surface_lateral_rays, (0,0))


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

def draw_rays(surface, start_pos, directions, angle, length):
    for d in directions:
        end_x, end_y = calculate_line_endpoints(start_pos[0], start_pos[1], angle + d, length)
        pygame.draw.line(surface, (0, 255, 0), start_pos, (end_x, end_y), 1)


if __name__ == '__main__':
    car = Car()

    game_iteration = 0
    front_rays_directions = [0, -30, 30]
    lateral_rays_directions = [-90, 90]


    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
        keys = pygame.key.get_pressed()
        move_player(car, keys)


        surface_front_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
        surface_lateral_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
        surfaces_to_draw = [surface_front_rays, surface_lateral_rays]

        draw(WIN, surfaces_to_draw, car)


        mask_front_rays = pygame.mask.from_surface(surface_front_rays.convert_alpha())
        if mask_front_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            print("Danger: car is close to the wall! (front side)")
        mask_lateral_rays = pygame.mask.from_surface(surface_lateral_rays.convert_alpha())
        if mask_lateral_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            print("Danger: car is close to the wall! (lateral side)")


        if car.collide(TRACK_BORDER_MASK) != None:
            car.hit_wall()
            game_iteration = game_iteration + 1
            print("Started a new game iteration. Iteration #" + str(game_iteration))

    
        pygame.display.update()


    pygame.quit()
