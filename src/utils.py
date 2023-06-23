import pygame
import math

def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_left, angle, scale_rec=True):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)

    if abs(angle) % 90 > 5 and scale_rec:
        new_rect = new_rect.scale_by(0.5)
    return new_rect

def calculate_rect_distance(center1, center2):
    return math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)

def calculate_angle(center1, center2):
    dx = center2[0] - center1[0]
    dy = center2[1] - center1[1]
    rads = math.atan2(-dy, dx)
    degrees = math.degrees(rads) - 90
    if degrees >= 360:
        degrees = degrees - 360
    elif degrees <= 0:
        degrees = degrees + 360 

    return degrees

def normalize_value(value, min, max):
    return (value - min) / (max - min)

