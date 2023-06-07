import pygame
import math
import random
from utils import scale_image, blit_rotate_center, calculate_rect_distance
from car import PlayerCar

pygame.init()

RESOURCE_PATH = './../resources/'
CAR = scale_image(pygame.image.load(RESOURCE_PATH + "green-car.png"), 0.75)

WIDTH, HEIGHT = 640, 480
BG_COLOR = (115, 118, 122)
PARKING_SPACE_COLOR = (0, 255, 0)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
WIN.fill(BG_COLOR)

BORDER_DOWN = pygame.Rect(0, 0, 100000, 100)
BORDER_DOWN_MASK = pygame.mask.Mask((BORDER_DOWN.width, BORDER_DOWN.height), True)

global START_AGAIN
START_AGAIN = True

pygame.display.set_caption("AI Parking Simulator")
FPS = 60


def draw(win, player_car):
    WIN.fill(BG_COLOR)
    pygame.draw.rect(WIN, PARKING_SPACE_COLOR, parking_space)
    WIN.blit(font.render(text, True, (0, 0, 0)), (WIDTH - 60, 10))
    player_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

def spawn_parking_space(car_agent):
    car_center = car_agent.get_center(WIN)
    while True:
        if random.random() < 0.5:
            parking_space = pygame.Rect(random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80), CAR.get_width() + 20, CAR.get_height() + 20)
        else:
            parking_space = pygame.Rect(random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80), CAR.get_height() + 20, CAR.get_width() + 20)
        
        if calculate_rect_distance(parking_space.center, car_center) > 100:
            return parking_space

def out_of_bounds(car_agent):
    if(car_agent.x < 0 or car_agent.y < 0 or car_agent.x > WIDTH - car_agent.img.get_width() - 10 or car_agent.y > HEIGHT - car_agent.img.get_height()):
        global START_AGAIN 
        START_AGAIN = True

run = True
clock = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT, 1000)

while START_AGAIN:
    START_AGAIN = False
    car_agent = PlayerCar(4, 4, CAR, (random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80)))
    parking_space = spawn_parking_space(car_agent)
    counter, text = 10, '10'.rjust(3)
    font = pygame.font.SysFont('Consolas', 30)

    while run:
        clock.tick(FPS)
        draw(WIN, car_agent)

        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                counter -= 1
                text = str(counter).rjust(3)
                if counter == 0:
                    START_AGAIN = True
                    break
            if event.type == pygame.QUIT:
                run = False
                break

        move_player(car_agent)
        out_of_bounds(car_agent)
        if car_agent.is_parked(WIN, parking_space):
            START_AGAIN = True

        if START_AGAIN:
            break

    if not run:
        pygame.quit()
