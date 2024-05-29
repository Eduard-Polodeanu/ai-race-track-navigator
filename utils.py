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

def calculate_distance(start_point, end_point):
    cateta1 = abs(end_point[0] - start_point[0])
    cateta2 = abs(end_point[1] - start_point[1])
    distance = int(math.sqrt(cateta1*cateta1 + cateta2*cateta2))
    return distance
