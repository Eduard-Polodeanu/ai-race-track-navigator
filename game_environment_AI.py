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

class Direction(Enum):
    FORWARD = 1
    BACKWARDS = 2
    LEFT = 3
    RIGHT = 4
    NONE = 5


class GameEnvironmentAI:
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

    def play_step(self, action):
        self.game_iteration += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print('Final score: ', self.score)
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = pygame.mouse.get_pos()
                self.checkpoint_pos.append(click_pos)
        

        self.move_AI(action)


        # wall collision
        reward = 0
        is_game_over = False
        if self.car.collide(TRACK_BORDER_MASK) != None:
            is_game_over = True
            reward = -10
            return reward, is_game_over, self.score
        
        # checkpoint collision
        if self.all_checkpoints and is_point_on_line(self.car.center_pos, self.all_checkpoints[0], max(self.car.img.get_width(), self.car.img.get_height())/2):
            del self.all_checkpoints[0]
            self.score += 10
            reward = 10

        # finish line collision
        if not self.all_checkpoints and is_point_on_line(self.car.center_pos, self.finish_line_pos, max(self.car.img.get_width(), self.car.img.get_height())/2):
            self.reset_checkpoints()

        self.draw()
        self.clock.tick(FPS)


        return reward, is_game_over, self.score


    def draw(self):
        self.window.blit(TRACK, (0, 0))
        self.window.blit(TRACK_BORDER, (0, 0))

        self.car.draw(self.window)

        surface_front_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
        surface_lateral_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
        surfaces_to_draw = [surface_front_rays, surface_lateral_rays]
        
        draw_rays(surfaces_to_draw[0], self.car.center_pos, self.car.front_rays_directions, self.car.angle, 50)
        draw_rays(surfaces_to_draw[1], self.car.center_pos, self.car.lateral_rays_directions, self.car.angle, 35) 
        self.window.blit(surface_front_rays, (0,0))
        self.window.blit(surface_lateral_rays, (0,0))

        """
        mask_front_rays = pygame.mask.from_surface(surface_front_rays.convert_alpha())
        if mask_front_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            print("Danger: car is close to the wall! (front side)")
        mask_lateral_rays = pygame.mask.from_surface(surface_lateral_rays.convert_alpha())
        if mask_lateral_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            print("Danger: car is close to the wall! (lateral side)")
        """
        
        self.checkpoint_pos, self.all_checkpoints = draw_checkpoint_onclick(self.window, self.checkpoint_pos, self.all_checkpoints)        
        pygame.draw.line(self.window, (0, 0, 255), self.finish_line_pos[0], self.finish_line_pos[1], 3)
        

        pygame.display.flip()


    def move_AI(self, action):
    
        self.move_direction = Direction.NONE
        self.steer_direction = Direction.NONE
        
        # Forward	            1
        # Backwards	            2
        # Turn Left         	3
        # Turn Right            4
        # Forward + left 	    5
        # Forward + right      	6
        # Backwards + left      7
        # Backwards + right     8
        # No action             9
        
        if action == 1:
            self.move_direction = Direction.FORWARD
        elif action == 2:
            self.move_direction == Direction.BACKWARDS
        elif action == 3:
            self.steer_direction == Direction.LEFT
        elif action == 4:
            self.steer_direction == Direction.RIGHT
        elif action == 5:
            self.move_direction = Direction.FORWARD
            self.steer_direction = Direction.LEFT
        elif action == 6:
            self.move_direction = Direction.FORWARD
            self.steer_direction = Direction.RIGHT
        elif action == 7:
            self.move_direction = Direction.BACKWARDS
            self.steer_direction = Direction.LEFT
        elif action == 8:
            self.move_direction = Direction.BACKWARDS
            self.steer_direction = Direction.RIGHT
        elif action == 9:
            self.car.reduce_speed()


        if self.move_direction == Direction.FORWARD:
            self.car.move_forward()
            if self.steer_direction == Direction.LEFT:
                self.car.rotate(left=True)
            elif self.steer_direction == Direction.RIGHT:
                self.car.rotate(right=True)
        elif self.move_direction == Direction.BACKWARDS:
            self.car.move_backward()
            if self.steer_direction == Direction.LEFT:
                self.car.rotate(right=True)
            elif self.steer_direction == Direction.RIGHT:
                self.car.rotate(left=True)
        else:
            if self.steer_direction == Direction.LEFT:
                self.car.rotate(left=True)
            elif self.steer_direction == Direction.RIGHT:
                self.car.rotate(right=True)
        
