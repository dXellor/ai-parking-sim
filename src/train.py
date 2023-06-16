from rlenv import ParkingEnv
from stable_baselines3 import PPO

RESOURCE_PATH = './../models/'

if __name__ == "__main__":
    env = ParkingEnv(False)
    model = PPO("MlpPolicy", env, verbose=1)
    
    try:
        model.load(RESOURCE_PATH + "parking-ppo-v1-nobs")   
    except:
        print("Could not load model file. New file will be created")

    i = 0
    while True:
        print(f"Run {i}")
        i += 1
        model.learn(total_timesteps=25000)
        model.save("parking-ppo-v1-nobs")    