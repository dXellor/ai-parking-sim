import torch
from torch import nn
import torch.nn.functional as f
import numpy as np

class FeedForwardNN(nn.Module):
    def __init__(self, input_num, output_num) -> None:
        super(FeedForwardNN, self).__init__()

        self.layer1 = nn.Linear(input_num, 64)
        self.layer2 = nn.Linear(64, 64)
        self.layer3 = nn.Linear(64, output_num)

    def forward(self, obs):
        if(isinstance(obs, np.ndarray)):
            obs = torch.tensor(obs, dtype=torch.float)

        activ1 = f.selu(self.layer1(obs))
        activ2 = f.selu(self.layer2(activ1))
        out = self.layer3(activ2)

        return out
