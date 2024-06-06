from enum import Enum
import pygame
from car import Car
from utils import draw_checkpoint_onclick, draw_rays, is_point_on_line

pygame.init()

TRACK = pygame.image.load("assets/track.png")
TRACK_BORDER = pygame.image.load("assets/track-hitbox.png")
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

WIN_SIZE = (1280, 720)
FPS = 60

surface_front_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
surface_lateral_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)

class Direction(Enum):
    FORWARD = 1
    BACKWARDS = 2
    LEFT = 3
    RIGHT = 4
    NONE = 5


class GameEnvironment:
    def __init__(self, car):
        self.window = pygame.display.set_mode(WIN_SIZE, flags=pygame.SCALED, vsync=1)
        pygame.display.set_caption("Track navigator")
        self.clock = pygame.time.Clock()
        self.car = car
        self.reset()

    def reset(self):
        self.game_iteration = 0
        self.car.reset()
        self.score = 0
        self.reset_checkpoints()
        self.finish_line_pos = [(205, 30), (205, 130)]

    def reset_checkpoints(self):
        self.checkpoint_pos = []
        self.all_checkpoints = [[(721, 9), (726, 159)], [(803, 10), (808, 154)], [(900, 8), (890, 148)]]

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print('Final score: ', self.score)
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = pygame.mouse.get_pos()
                self.checkpoint_pos.append(click_pos)

        self.keys = pygame.key.get_pressed()
    
        self.move_direction = Direction.NONE
        self.steer_direction = Direction.NONE
        
        if self.keys[pygame.K_w]:
            self.move_direction = Direction.FORWARD
        elif self.keys[pygame.K_s]:
            self.move_direction = Direction.BACKWARDS
        
        if self.keys[pygame.K_a]:
            self.steer_direction = Direction.LEFT
        elif self.keys[pygame.K_d]:
            self.steer_direction = Direction.RIGHT
        

        self.move_player()


        is_game_over = False
        if self.car.collide(TRACK_BORDER_MASK) != None:
            self.reset()
            self.score -= 10
            # is_game_over = True
            # return is_game_over, self.score
        
        # checkpoint collision
        if self.all_checkpoints and is_point_on_line(self.car.center_pos, self.all_checkpoints[0], max(self.car.img.get_width(), self.car.img.get_height())/2):
            del self.all_checkpoints[0]
            self.score += 10

        # finish line collision
        if not self.all_checkpoints and is_point_on_line(self.car.center_pos, self.finish_line_pos, max(self.car.img.get_width(), self.car.img.get_height())/2):
            self.reset_checkpoints()

        # rays collision
        mask_front_rays = pygame.mask.from_surface(surface_front_rays.convert_alpha())
        if mask_front_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            self.car.danger[0] = True
            # print("Danger: car is close to the wall! (front side)")
        else:
            self.car.danger[0] = False
            
        mask_lateral_rays = pygame.mask.from_surface(surface_lateral_rays.convert_alpha())
        if mask_lateral_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            self.car.danger[1] = True
            # print("Danger: car is close to the wall! (lateral side)")
        else:
            self.car.danger[1] = False


        self.draw()
        self.clock.tick(FPS)


        return is_game_over, self.score

    def draw(self):
        self.window.blit(TRACK, (0, 0))
        self.window.blit(TRACK_BORDER, (0, 0))

        self.car.draw(self.window)

        surface_front_rays.fill((0,0,0,0))     # reset ray surface
        surface_lateral_rays.fill((0,0,0,0))
        draw_rays(surface_front_rays, self.car.center_pos, self.car.front_rays_directions, self.car.angle, 50)
        draw_rays(surface_lateral_rays, self.car.center_pos, self.car.lateral_rays_directions, self.car.angle, 35) 
        self.window.blit(surface_front_rays, (0,0))
        self.window.blit(surface_lateral_rays, (0,0))
        
        self.checkpoint_pos, self.all_checkpoints = draw_checkpoint_onclick(self.window, self.checkpoint_pos, self.all_checkpoints)        
        pygame.draw.line(self.window, (0, 0, 255), self.finish_line_pos[0], self.finish_line_pos[1], 3)
        
        pygame.display.flip()


    def move_player(self):
        is_moving = False
        
        if self.move_direction == Direction.FORWARD:
            is_moving = True
            self.car.move_forward()
        elif self.move_direction == Direction.BACKWARDS:
            is_moving = True
            self.car.move_backward()
        
        if self.steer_direction == Direction.LEFT:
            if self.move_direction == Direction.BACKWARDS:       # inverse steering when going backwards
                self.car.rotate(right=True)
            else:
                self.car.rotate(left=True) 
        elif self.steer_direction == Direction.RIGHT:
            if  self.move_direction == Direction.BACKWARDS:      # inverse steering when going backwards
                self.car.rotate(left=True)
            else:
                self.car.rotate(right=True) 
        
        if not is_moving:
            self.car.reduce_speed()

    
        

if __name__ == '__main__':
    car = Car()
    game = GameEnvironment(car)

    running = True
    while running:
        is_game_over, score = game.play_step()
        if is_game_over == True:
            running = False

    print('Final score: ', score)   # e degeaba daca resetez jocul la coliziune si nu returnez is_game_over in play_step()

    pygame.quit()
