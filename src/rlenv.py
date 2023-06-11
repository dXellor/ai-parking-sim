from gym import Env
from gym import spaces
from gym.utils.ezpickle import EzPickle
import pygame
import random
import numpy as np
from utils import scale_image, calculate_rect_distance
from car import PlayerCar

pygame.init()
DEBUG = False

RESOURCE_PATH = './../resources/'
CAR = scale_image(pygame.image.load(RESOURCE_PATH + "green-car.png"), 0.75)

WIDTH, HEIGHT = 640, 480
BG_COLOR = (115, 118, 122)
PARKING_SPACE_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (0, 0, 0)
OBSTACLE_NUM = 8

global START_AGAIN
START_AGAIN = True
FPS = 60

pygame.display.set_caption("AI Parking Simulator")

class ParkingEnv(Env, EzPickle):

    def __init__(self, verbose, spawnobstacles=False):
        EzPickle.__init__(self, verbose)
        self.verbose = verbose
        self.spawnobstacles = spawnobstacles 
        
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.window.fill(BG_COLOR)
        self.car = PlayerCar(4, 4, CAR, (random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80)))
        self.spawn_parking_space()
        if self.spawnobstacles:
            self.spawn_obstacles()
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.counter = 10
        self.text = str(self.counter).rjust(3)
        self.font = pygame.font.SysFont('Consolas', 30)

        self.reward = 0
        self.previous_reward = 0
        self.action_space = spaces.Box(
            np.array([-1, -1]).astype(np.float32),
            np.array([+1, +1]).astype(np.float32),
            #0.forward-backward, 1.left-right
        )

        self.observation_space = spaces.Box(np.array([0, 0, -10000, -1000, 0]), np.array([WIDTH, HEIGHT, 10000, 1000, HEIGHT**2+WIDTH**2]), shape=(5,))


    def step(self, action) :
        if action[0] > 0:
            self.car.move_forward()
        elif action[0] < 0:
            self.car.move_backward()
        else:
            self.car.reduce_speed()

        if action[1] > 0:
            self.car.rotate(right=True)
        elif action[1] < 0:
            self.car.rotate(left=True)

        self.state = np.array(
            [self.car.x, self.car.y, self.car.angle, self.car.vel, self.parking_space_distance()]
        )

        step_reward = 0
        terminate = False
        success = False
        if action is not None:
            self.reward = -0.2
            self.reward -= self.parking_space_distance() / 10

            self.reward -= self.previous_reward
            step_reward =  self.reward - self.previous_reward

            if self.out_of_bounds():
                terminate = True
                step_reward -= 100

            if self.spawnobstacles:
                if self.obstacle_collision():
                    terminate = True
                    step_reward -= 100

            if self.car.is_parked(self.window, self.parking_space):
                success = True
                step_reward += 1000
            
        self.render()
        info = {}

        return self.state, step_reward, terminate, success, info

    def render(self):

        self.clock.tick(FPS)
        self.draw()
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                self.counter -= 1
                self.text = str(self.counter).rjust(3)
    
    def reset(self):
        self.car = PlayerCar(4, 4, CAR, (random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80)))
        self.spawn_parking_space()
        if self.spawnobstacles:
            self.spawn_obstacles()
        self.counter = 10
        self.text = str(self.counter).rjust(3)
        self.font = pygame.font.SysFont('Consolas', 30)

        self.reward = 0
        self.previous_reward = 0

    def close(self):
        pygame.quit()

    def spawn_parking_space(self):
        while True:
            if random.random() < 0.5:
                self.parking_space = pygame.Rect(random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80), CAR.get_width() + 20, CAR.get_height() + 20)
            else:
                self.parking_space = pygame.Rect(random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80), CAR.get_height() + 20, CAR.get_width() + 20)
            
            if calculate_rect_distance(self.parking_space.center, self.car.get_center(self.window)) > 100:
                return self.parking_space
            
    def spawn_obstacles(self):
        self.obstacles = []
        while True:
            obstacle = pygame.Rect(random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80), 40, 40)

            if calculate_rect_distance(self.car.get_center(self.window), obstacle.center) > 50 and not obstacle.colliderect(self.parking_space):
                self.obstacles.append(obstacle)
            
            if len(self.obstacles) == OBSTACLE_NUM:
                return self.obstacles
            
    def parking_space_distance(self):
        return calculate_rect_distance(self.car.get_center(self.window), self.parking_space.center)
    
    def out_of_bounds(self):
        if self.car.x < 0 or self.car.y < 0 or self.car.x > WIDTH - self.car.img.get_width() - 10 or self.car.y > HEIGHT - self.car.img.get_height():
            return True
        return False

    def obstacle_collision(self):
        for o in self.obstacles:
            if self.car.get_rect(self.window).colliderect(o):
                return True
        return False
    
    def draw(self):
        self.window.fill(BG_COLOR)
        pygame.draw.rect(self.window, PARKING_SPACE_COLOR, self.parking_space)
        if DEBUG:
            pygame.draw.rect(self.window, (255, 255, 255), self.car.get_rect(self.window))

        if self.spawnobstacles:
            if self.obstacles:
                for o in self.obstacles:
                    pygame.draw.rect(self.window, OBSTACLE_COLOR, o)

        self.window.blit(self.font.render(self.text, True, (0, 0, 0)), (WIDTH - 60, 10))
        self.car.draw(self.window)
        pygame.display.update()


if __name__ == "__main__":
    action = np.array([0.0, 0.0])

    def register_input():
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            action[0] = -1
        elif keys[pygame.K_UP]:
            action[0] = 1
        else:
            action[0] = 0

        if keys[pygame.K_LEFT]:
            action[1] = -1
        elif keys[pygame.K_RIGHT]:
            action[1] = 1
        else:
            action[1] = 0

    env = ParkingEnv(False, True)
    quit = False
    while not quit:
        env.reset()
        total_reward = 0.0
        steps = 0
        restart = False
        while True:
            # register_input()
            action = env.action_space.sample()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True
                    break

            s, r, terminated, success, info = env.step(action)
            total_reward += r
            if steps % 200 == 0 or terminated or success:
                if DEBUG:
                    print(s)
                    print("\naction " + str([f"{x:+0.2f}" for x in action]))
                    print(f"step {steps} total_reward {total_reward:+0.2f}")       
            steps += 1
            if success:
                break
            if terminated or restart or quit:
                break

    env.close()