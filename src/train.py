from rlenv import ParkingEnv
from arguments import get_args
from stable_baselines3 import PPO, A2C

RESOURCE_PATH = './../models/'
ALG = "ppo"

def main(args):
    arg_error = False
    env = ParkingEnv(False, args.obstacles)
    if args.algorithm == "ppo":
        model = PPO("MlpPolicy", env, verbose=1, n_steps=512, gamma=0.95)
    elif args.algorithm == "a2c":
        model = A2C("MlpPolicy", env, verbose=1)
    else:
        print("Invalid argument for algorithm. Defaulting to ppo...")
        model = PPO("MlpPolicy", env, verbose=1)
        arg_error = True

    if args.model == "":
        model_path = RESOURCE_PATH + "parking-" + args.algorithm + ("-nobs" if args.obstacles == 0 else "-wobs")
    else:
        model_path = RESOURCE_PATH + args.model

    try:
        model = model.load(model_path, env)
    except:
        print("Could not load model file. New file will be created")

    print(f"\nConfiguration:\nAlgorithm: {ALG if arg_error else args.algorithm}\nObstacle number: {args.obstacles}\nNumber of timestamps per run: {args.timestamps}\nModel file: {model_path}\n")

    i = 0
    while True:
        print(f"Run {i}")
        i += 1
        model.learn(args.timestamps)
        model.save(model_path)  

if __name__ == "__main__":
    args = get_args()
    main(args)  