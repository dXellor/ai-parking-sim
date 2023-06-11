from ppo import PPO
from rlenv import ParkingEnv

if __name__ == "__main__":
    env = ParkingEnv(False, False)
    model = PPO(env)
    model.learn(10000000)