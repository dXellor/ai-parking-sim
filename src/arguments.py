import argparse

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--algorithm", help="rl algorithm [ppo, a2c]", type=str, default="ppo")
    parser.add_argument("-o", "--obstacles", help="number of obstacles", type=int, default=0)
    parser.add_argument("-m", "--model", help="load model from file", type=str, default="")
    parser.add_argument("-t", "--timestamps", help="number of timestamps in one run", type=int, default=25000)
    parser.add_argument("-p", "--play", help="let model play game without training", action="store_true")

    args = parser.parse_args()
    return args