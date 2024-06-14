import math
from matplotlib import pyplot as plt
from IPython import display
import pygame


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

# draw the image based on the rotation angle of the car
def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)

def calculate_line_endpoints(start_x, start_y, angle, length):
    radians = math.radians(angle)
    end_x = start_x + length * math.cos(radians)
    end_y = start_y - length * math.sin(radians)
    return end_x, end_y

def draw_rays(surface, start_pos, directions, angle, length):
    for d in directions:
        end_x, end_y = calculate_line_endpoints(start_pos[0], start_pos[1], angle + d, length)
        pygame.draw.line(surface, (0, 255, 0), start_pos, (end_x, end_y), 3)

def draw_checkpoint_onclick(win, checkpoint_pos, all_checkpoints):
    if len(checkpoint_pos) == 2:
        print("Checkpoint added: " + str(checkpoint_pos))
        all_checkpoints.append(checkpoint_pos)
        checkpoint_pos = []
    for i in range(0, len(all_checkpoints)):
        pygame.draw.line(win, (255, 0, 0), all_checkpoints[i][0], all_checkpoints[i][1], 3)
    return checkpoint_pos, all_checkpoints

def calculate_dist_points(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def calculate_midpoint(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    midpoint_x = (x1 + x2) / 2
    midpoint_y = (y1 + y2) / 2
    return (midpoint_x, midpoint_y)

def is_point_on_line(point, line_segment, tolerance=1):
    px, py = point
    (x1, y1), (x2, y2) = line_segment   

    cross_product = abs((x2 - x1) * (py - y1) - (px - x1) * (y2 - y1))      # produs vectorial intre (px, py) si (x1, y1);  daca e 0 punctul e coliniar pe segment; 

    line_length = calculate_dist_points(line_segment[0], line_segment[1])
    if line_length != 0:
        distance = cross_product / line_length
    else:
        distance = 0

    return distance <= tolerance

def calculate_angle(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    delta_x = x2 - x1
    delta_y = y2 - y1
    angle = math.atan2(delta_y, delta_x)  # Angle in radians
    angle_degrees = math.degrees(angle)  # Convert angle to degrees (optional)
    return angle_degrees


plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)