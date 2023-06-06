import pygame
import math
import random
from utils import scale_image, blit_rotate_center

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

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def set_start_position(self, position):
        self.x, self.y = position

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

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

        if(self.x < 0 or self.y < 0 or self.x > WIDTH - CAR.get_width() - 10 or self.y > HEIGHT - CAR.get_height()):
            global START_AGAIN 
            START_AGAIN = True
            self.reset()

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
        car_rect = blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        return parking_space.contains(car_rect)
    
    def get_center(self, win):
        return blit_rotate_center(win, self.img, (self.x, self.y), self.angle).center
    

class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = (0,0)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def crash(self):
        self.vel = -self.vel * 0.3
        self.move()



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

def calculate_rect_distance(center1, center2):
    return math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)

def spawn_parking_space(car_agent):
    car_center = car_agent.get_center(WIN)
    while True:
        if random.random() < 0.5:
            parking_space = pygame.Rect(random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80), CAR.get_width() + 20, CAR.get_height() + 20)
        else:
            parking_space = pygame.Rect(random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80), CAR.get_height() + 20, CAR.get_width() + 20)
        
        if calculate_rect_distance(parking_space.center, car_center) > 100:
            return parking_space

run = True
clock = pygame.time.Clock()
car_agent = PlayerCar(4, 4)
pygame.time.set_timer(pygame.USEREVENT, 1000)

while START_AGAIN:
    START_AGAIN = False
    car_agent.set_start_position((random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80)))
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
        if car_agent.is_parked(WIN, parking_space):
            START_AGAIN = True

        if START_AGAIN:
            car_agent.reset()
            break

    if not run:
        pygame.quit()
