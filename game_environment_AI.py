import pygame
from enum import Enum
from utils import calculate_angle, calculate_dist_points, calculate_midpoint, draw_checkpoint_onclick, draw_rays, is_point_on_line

pygame.init()

TRACK = pygame.image.load("assets/track2.png")
TRACK_BORDER = pygame.image.load("assets/track-hitbox2.png")
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

WIN_SIZE = (1280, 720)
FPS = 60

surface_front_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
surface_left_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)
surface_right_rays = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1]), pygame.SRCALPHA)


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
        self.dist_to_checkpoint = 0
        self.distances_list = []
        self.same_consecutive_dist = 0
        self.angle_to_checkpoint = 0
        # self.turns_of_high_vel = 0
        # self.turns_of_low_vel = 0
        self.reward = 0
        # self.penality = 0

    def reset_checkpoints(self):
        self.checkpoint_pos = []
        self.finish_line_pos = [(604, 49), (600, 185)]
        self.all_checkpoints = [[(738, 63), (712, 186)], [(848, 76), (799, 220)], [(968, 121), (870, 244)], [(903, 282), (1127, 272)], [(862, 347), (1033, 455)], [(762, 407), (818, 556)], [(631, 422), (624, 556)], [(503, 390), (421, 534)], [(419, 344), (234, 447)], [(392, 282), (147, 303)], [(451, 226), (262, 129)], [(525, 195), (452, 42)]]

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
        is_game_over = False
        if self.car.collide(TRACK_BORDER_MASK) != None:
            is_game_over = True
            self.reward += -10
            print("reward this cycle: ", self.reward)
            return self.reward, is_game_over, self.score
        
        # checkpoint collision
        if self.all_checkpoints and is_point_on_line(self.car.center_pos, self.all_checkpoints[0], max(self.car.img.get_width(), self.car.img.get_height())/2):
            del self.all_checkpoints[0]
            self.score += 10
            self.reward += 3
            self.same_consecutive_dist = 0


        # finish line collision
        if not self.all_checkpoints and is_point_on_line(self.car.center_pos, self.finish_line_pos, max(self.car.img.get_width(), self.car.img.get_height())/2):
            self.reset_checkpoints()

        # rays collision
        mask_front_rays = pygame.mask.from_surface(surface_front_rays.convert_alpha())
        if mask_front_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            self.car.danger[0] = True
            self.reward += -0.05
            # print("Danger: car is close to the wall! (front side)")
        else:
            self.car.danger[0] = False
        mask_left_rays = pygame.mask.from_surface(surface_left_rays.convert_alpha())
        if mask_left_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            self.car.danger[1] = True
            self.reward += -0.005
            # print("Danger: car is close to the wall! (left side)")
        else:
            self.car.danger[1] = False
        mask_right_rays = pygame.mask.from_surface(surface_left_rays.convert_alpha())
        if mask_right_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            self.car.danger[2] = True
            self.reward += -0.005
            # print("Danger: car is close to the wall! (right side)")
        else:
            self.car.danger[2] = False


        # distance to next checkpoint
        if self.all_checkpoints:
            ck = self.all_checkpoints[0]
            checkpoint_midpoint = calculate_midpoint(ck[0], ck[1])
            self.dist_to_checkpoint = int(calculate_dist_points(checkpoint_midpoint, (self.car.x, self.car.y)))
            self.distances_list.append(self.dist_to_checkpoint)
            if len(self.distances_list) > 1:
                if self.distances_list[-1] == self.distances_list[-2]:
                    self.same_consecutive_dist += 1
                else:
                    self.same_consecutive_dist = 0
        if self.same_consecutive_dist == 250:   # change hardcode to const
            is_game_over = True
            self.reward = -5
            #print("reward this cycle: ", self.reward)
            return self.reward, is_game_over, self.score
        

        self.angle_to_checkpoint = calculate_angle(self.car.center_pos, checkpoint_midpoint)
        if abs(self.angle_to_checkpoint) < 45:
            self.reward += 0.001
        else:
            self. reward += -0.005 


        
        """
        if self.car.vel < 1 and self.car.vel >= 0:   # change hardcode to const
            self.turns_of_low_vel += 1
        if self.turns_of_low_vel == 75:    # change hardcode to const
            self.penality += -0.1
            self.turns_of_low_vel = 0
            print("LOW SPEED PENALITY")
            print("current penality: ", self.penality)
        
        
        if self.car.vel >= 2:   # change hardcode to const
            self.turns_of_high_vel += 1
        if self.turns_of_high_vel == 200:    # change hardcode to const
            self.reward += 0.1
            self.turns_of_high_vel = 0
            #print("HIGH SPEED REWARD")
            #print("new reward: ", self.reward)
        """



        self.draw()
        self.clock.tick(FPS)

        print("reward this cycle: ", self.reward)
        return self.reward, is_game_over, self.score


    def draw(self):
        self.window.blit(TRACK, (0, 0))
        self.window.blit(TRACK_BORDER, (0, 0))

        self.car.draw(self.window)

        surface_front_rays.fill((0,0,0,0))     # reset ray surface
        surface_left_rays.fill((0,0,0,0))
        surface_right_rays.fill((0,0,0,0))
        draw_rays(surface_front_rays, self.car.center_pos, self.car.front_rays_directions, self.car.angle, 150)
        draw_rays(surface_left_rays, self.car.center_pos, self.car.left_rays_directions, self.car.angle, 35) 
        draw_rays(surface_right_rays, self.car.center_pos, self.car.right_rays_directions, self.car.angle, 35) 
        self.window.blit(surface_front_rays, (0,0))
        self.window.blit(surface_left_rays, (0,0))
        self.window.blit(surface_right_rays, (0,0))

        self.checkpoint_pos, self.all_checkpoints = draw_checkpoint_onclick(self.window, self.checkpoint_pos, self.all_checkpoints)        
        pygame.draw.line(self.window, (0, 0, 255), self.finish_line_pos[0], self.finish_line_pos[1], 1)
        
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
        """
        elif action == 7:
            self.car.reduce_speed()
        elif action == 8:
            self.move_direction = Direction.BACKWARDS
            self.steer_direction = Direction.LEFT
        elif action == 9:
            self.move_direction = Direction.BACKWARDS
            self.steer_direction = Direction.RIGHT
        """


        if self.move_direction == Direction.FORWARD:
            self.car.move_forward()
            if self.steer_direction == Direction.LEFT:
                self.car.rotate(left=True)
            elif self.steer_direction == Direction.RIGHT:
                self.car.rotate(right=True)
        elif self.move_direction == Direction.BACKWARDS:
            self.car.move_backward()
            """
            if self.steer_direction == Direction.LEFT:
                self.car.rotate(right=True)
            elif self.steer_direction == Direction.RIGHT:
                self.car.rotate(left=True) 
            """
        elif self.steer_direction == Direction.LEFT:
            self.car.rotate(left=True)
        elif self.steer_direction == Direction.RIGHT:
            self.car.rotate(right=True)
        
