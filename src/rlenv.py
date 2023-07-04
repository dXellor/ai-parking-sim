from gymnasium import Env
from gymnasium import spaces
import pygame
import random
import numpy as np
from utils import scale_image, calculate_rect_distance, calculate_angle, normalize_value
from car import PlayerCar
import math

pygame.init()
DEBUG = False

RESOURCE_PATH = './../resources/'
CAR = scale_image(pygame.image.load(RESOURCE_PATH + "green-car.png"), 0.75)

WIDTH, HEIGHT = 640, 480
BG_COLOR = (115, 118, 122)
PARKING_SPACE_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (0, 0, 0)

global START_AGAIN
START_AGAIN = True
FPS = 60

pygame.display.set_caption("AI Parking Simulator")

class ParkingEnv(Env):

    def __init__(self, verbose, obstacle_number = 0, counter = 30):
        self.verbose = verbose
        
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.window.fill(BG_COLOR)
        self.car = PlayerCar(4, 4, CAR, (random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80)))
        self.spawn_parking_space()
        self.obstacle_number = obstacle_number
        if self.obstacle_number > 0:
            self.spawn_obstacles()
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.counter = counter
        self.text = str(self.counter).rjust(3)
        self.font = pygame.font.SysFont('Consolas', 30)
        self.looking_at_parking = False

        self.reward = 0
        self.previous_reward = 0
        # self.action_space = spaces.MultiDiscrete(np.array([3, 3]))
        self.action_space = spaces.Discrete(4)

        if self.obstacle_number <= 0:
            # x and y error from parking space center, angle error and car velocity
            self.observation_space = spaces.Box(low=0, high=1, shape=(4,))
        else:
            self.observation_space = spaces.Box(low=0, high=1, shape=(4 + self.obstacle_number,))

    def step(self, action):
        if action == 0:
            self.car.move_forward()
        elif action == 1:
            self.car.move_backward()
        else:
            self.car.reduce_speed()

        if action == 2:
            self.car.rotate(right=True)
        elif action == 3:
            self.car.rotate(left=True)

        self.state = np.array(
            [
                normalize_value(abs(self.car.x - self.parking_space.center[0]), 0, WIDTH),
                normalize_value(abs(self.car.y - self.parking_space.center[1]), 0, HEIGHT),
                normalize_value(abs(self.angle_to_parking_space() - self.car.angle), 0, 359),
                normalize_value(self.car.vel, -4, 4),
            ]
        )

        if self.obstacle_number > 0:
            obs = []
            for o in self.obstacles:
                distance = self.obstacle_distance(o)
                if distance <= 150:
                    obs.append(normalize_value(distance, 0, 150))
                else:
                    obs.append(1)
            self.state = np.append(self.state, np.array(obs))

        step_reward = 0
        terminate = False
        success = False
        if action is not None:
            parking_distance = self.parking_space_distance()
            step_reward -= parking_distance/100
            # if abs(self.angle_to_parking_space() - self.car.angle) < 3 or abs(self.angle_to_parking_space() - self.car.angle) > 356:
            #     if not self.looking_at_parking:
            #         step_reward += 100
            #         self.looking_at_parking = True
            # else:
            #     if self.looking_at_parking:
            #         step_reward -= 10
            #     else:
            #         step_reward -= 1

            if self.car.vel < 0.5 and parking_distance > 20 and self.looking_at_parking:
                step_reward -= 1
            if self.car.vel > 0.8 and parking_distance < 20:
                step_reward -= 1

            if self.out_of_bounds():
                step_reward -= 1000
                self.looking_at_parking = False
                self.car.reset()

            if self.obstacle_number > 0:
                if self.obstacle_collision():
                    self.car.reset()
                    step_reward -= 100

            # if self.counter == 0:
            #     step_reward -= 100
            #     terminate = True

            if self.car.is_parked(self.window, self.parking_space):
                success = True
                step_reward += 1000000

        self.render()
        self.previous_reward = self.reward
        self.reward = self.reward + step_reward       
        info = {}

        return self.state, step_reward, terminate, success, info

    def render(self):

        self.clock.tick(FPS)
        self.draw()
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                self.counter -= 1
                self.text = str(self.counter).rjust(3)
    
    def reset(self, seed=None):
        self.car = PlayerCar(4, 4, CAR, (random.randint(CAR.get_height(), WIDTH - 80), random.randint(CAR.get_height(), HEIGHT-80)))
        self.spawn_parking_space()
        if self.obstacle_number > 0:
            self.spawn_obstacles()
        self.counter = 30
        self.text = str(self.counter).rjust(3)
        self.font = pygame.font.SysFont('Consolas', 30)
        self.looking_at_parking = False

        self.reward = 0
        self.previous_reward = 0

        self.state = np.array(
            [    
                normalize_value(abs(self.car.x - self.parking_space.center[0]), 0, WIDTH),
                normalize_value(abs(self.car.y - self.parking_space.center[1]), 0, HEIGHT),
                normalize_value(abs(self.angle_to_parking_space() - self.car.angle), 0, 359),
                normalize_value(self.car.vel, -4, 4),
            ]
        )

        if self.obstacle_number > 0:
            obs = []
            for o in self.obstacles:
                distance = self.obstacle_distance(o)
                if distance <= 150:
                    obs.append(normalize_value(distance, 0, 150))
                else:
                    obs.append(1)
            self.state = np.append(self.state, np.array(obs))

        return self.state, 0

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
            
            if len(self.obstacles) == self.obstacle_number:
                return self.obstacles
            
    def parking_space_distance(self):
        return calculate_rect_distance(self.car.get_center(self.window), self.parking_space.center)
    
    def angle_to_parking_space(self):
        return calculate_angle(self.car.get_center(self.window), self.parking_space.center)

    def obstacle_distance(self, obstacle):
        return calculate_rect_distance(self.car.get_center(self.window), obstacle.center)

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

        if self.obstacle_number:
            if self.obstacles:
                for o in self.obstacles:
                    pygame.draw.rect(self.window, OBSTACLE_COLOR, o)

        self.window.blit(self.font.render(self.text, True, (0, 0, 0)), (WIDTH - 60, 10))
        reward_text = f"R:{self.reward:.4f}"
        self.window.blit(self.font.render(reward_text, True, (0, 0, 0)), (10, 10))
        self.car.draw(self.window)
        pygame.display.update()


if __name__ == "__main__":

    def register_input():
        action = None
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            action = 1
        elif keys[pygame.K_UP]:
            action = 0

        if keys[pygame.K_LEFT]:
            action = 3
        elif keys[pygame.K_RIGHT]:
            action = 2

        return action

    env = ParkingEnv(False, 10)
    quit = False
    while not quit:
        env.reset()
        total_reward = 0.0
        steps = 0
        restart = False
        while True:
            action = register_input()
            # action = env.action_space.sample()

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