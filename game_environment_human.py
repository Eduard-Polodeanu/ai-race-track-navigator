from enum import Enum
import pygame
from car import Car
from utils import calculate_dist_points, calculate_midpoint, draw_checkpoint_onclick, draw_rays, is_point_on_line

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

    def reset_checkpoints(self):
        self.checkpoint_pos = []
        # self.all_checkpoints = [[(661, 9), (666, 159)], [(761, 10), (766, 154)], [(861, 8), (866, 148)], [(961, 8), (966, 148)], [(1035, 18), (1015, 130)], [(1113, 69), (1052, 151)], [(1076, 191), (1178, 147)], [(1089, 238), (1188, 232)], [(1075, 303), (1174, 306)], [(1174, 331), (1074, 390)], [(1222, 342), (1187, 432)], [(1216, 468), (1277, 466)], [(1196, 505), (1257, 582)], [(1147, 510), (1156, 612)], [(1056, 539), (1093, 624)], [(932, 588), (935, 678)], [(905, 550), (828, 539)], [(932, 474), (856, 442)], [(891, 329), (973, 300)], [(827, 221), (842, 308)], [(612, 307), (646, 379)], [(530, 313), (503, 390)], [(455, 255), (383, 328)], [(288, 202), (334, 284)], [(214, 335), (298, 339)], [(241, 401), (347, 414)], [(236, 450), (292, 504)], [(174, 463), (129, 564)], [(138, 419), (65, 454)], [(75, 264), (4, 295)], [(7, 133), (93, 187)], [(163, 30), (174, 128)]]
        # self.all_checkpoints = [[(961, 8), (966, 148)], [(1035, 18), (1015, 130)], [(1113, 69), (1052, 151)], [(1076, 191), (1178, 147)], [(1089, 238), (1188, 232)], [(1075, 303), (1174, 306)], [(1174, 331), (1074, 390)], [(1222, 342), (1187, 432)], [(1216, 468), (1277, 466)], [(1196, 505), (1257, 582)], [(1147, 510), (1156, 612)], [(1056, 539), (1093, 624)], [(932, 588), (935, 678)], [(905, 550), (828, 539)], [(932, 474), (856, 442)], [(891, 329), (973, 300)], [(827, 221), (842, 308)], [(612, 307), (646, 379)], [(530, 313), (503, 390)], [(455, 255), (383, 328)], [(288, 202), (334, 284)], [(214, 335), (298, 339)], [(241, 401), (347, 414)], [(236, 450), (292, 504)], [(174, 463), (129, 564)], [(138, 419), (65, 454)], [(75, 264), (4, 295)], [(7, 133), (93, 187)], [(163, 30), (174, 128)]]
        self.finish_line_pos = [(604, 49), (600, 185)]
        self.all_checkpoints = [[(738, 63), (712, 186)], [(848, 76), (799, 220)], [(968, 121), (870, 244)], [(903, 282), (1127, 272)], [(862, 347), (1033, 455)], [(762, 407), (818, 556)], [(631, 422), (624, 556)], [(503, 390), (421, 534)], [(419, 344), (234, 447)], [(392, 282), (147, 303)], [(451, 226), (262, 129)], [(525, 195), (452, 42)]]

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
            print(self.all_checkpoints)
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
        mask_left_rays = pygame.mask.from_surface(surface_left_rays.convert_alpha())
        if mask_left_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            self.car.danger[1] = True
            # print("Danger: car is close to the wall! (left side)")
        else:
            self.car.danger[1] = False
        mask_right_rays = pygame.mask.from_surface(surface_left_rays.convert_alpha())
        if mask_right_rays.overlap(TRACK_BORDER_MASK, (0,0)):
            self.car.danger[2] = True
            # print("Danger: car is close to the wall! (right side)")
        else:
            self.car.danger[2] = False

        # distance to next checkpoint
        if self.all_checkpoints:
            ck = self.all_checkpoints[0]
            checkpoint_midpoint = calculate_midpoint(ck[0], ck[1])
            self.dist_to_checkpoint = int(calculate_dist_points(checkpoint_midpoint, (self.car.x, self.car.y)))
            # print(self.dist_to_checkpoint)

        self.draw()
        self.clock.tick(FPS)


        return is_game_over, self.score

    def draw(self):
        self.window.blit(TRACK, (0, 0))
        self.window.blit(TRACK_BORDER, (0, 0))

        self.car.draw(self.window)

        surface_front_rays.fill((0,0,0,0))     # reset ray surface
        surface_left_rays.fill((0,0,0,0))
        surface_right_rays.fill((0,0,0,0))
        draw_rays(surface_front_rays, self.car.center_pos, self.car.front_rays_directions, self.car.angle, 50)
        draw_rays(surface_left_rays, self.car.center_pos, self.car.left_rays_directions, self.car.angle, 15) 
        draw_rays(surface_right_rays, self.car.center_pos, self.car.right_rays_directions, self.car.angle, 15) 
        self.window.blit(surface_front_rays, (0,0))
        self.window.blit(surface_left_rays, (0,0))
        self.window.blit(surface_right_rays, (0,0))
        
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
