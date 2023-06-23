import pygame
import math
from utils import blit_rotate_center
import random

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
            if self.angle >= 360:
                self.angle = self.angle - 360
        elif right:
            self.angle -= self.rotation_vel
            if self.angle <= 0:
                self.angle = self.angle + 360

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

    def is_parked(self, win, parking_space):
        car_rect = blit_rotate_center(win, self.img, (self.x, self.y), self.angle, False)
        return parking_space.contains(car_rect)
    
    def get_center(self, win):
        return blit_rotate_center(win, self.img, (self.x, self.y), self.angle).center
    
    def get_rect(self, win):
        return blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

class PlayerCar(AbstractCar):

    def __init__(self, max_vel, rotation_vel, car_img, start_position):
        self.IMG = car_img
        self.START_POS = start_position
        super().__init__(max_vel, rotation_vel)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def crash(self):
        self.vel = -self.vel * 0.3
        self.move()