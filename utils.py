import math
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
        pygame.draw.line(surface, (0, 255, 0), start_pos, (end_x, end_y), 1)