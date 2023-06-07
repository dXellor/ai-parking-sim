import torch
import torch.nn as nn
from network import FeedForwardNN
from torch.distributions import MultivariateNormal
from torch.optim import Adam
import numpy as np

class PPO():
    def __init__(self, env):
        self._init_hyperparams()
        
        self.env = env
        self.obs_dim = env.observation_space.shape[0]
        self.act_dim = env.action_space.shape[0]

        self.actor = FeedForwardNN(self.obs_dim, self.act_dim)
        self.actor_optimizer = Adam(self.actor.parameters(), lr=self.lr)
        self.critic = FeedForwardNN(self.obs_dim, 1)
        self.critic_optimzer = Adam(self.critic.parameters(), lr=self.lr)

        self.cov_var = torch.full(size=(self.act_dim, ), fill_value=0.5)
        self.cov_mat = torch.diag(self.cov_var)

    def _init_hyperparams(self):
        self.timestamps_per_batch = 4800
        self.max_timestamps_per_episode = 1600
        self.gamma = 0.95
        self.updates_per_itter = 5
        self.clip = 0.2

        self.lr = 0.005

    def get_action(self, obs):
        mean = self.actor(obs)
        dist = MultivariateNormal(mean, self.cov_mat)

        action = dist.sample()
        log_prob = dist.log_prob(action)

        return action.detach().numpy(), log_prob.detach()
    
    def compute_rtgs(self, batch_rews):
        batch_rtgs = []

        for ep_rews in reversed(batch_rews):
            discounted_reward = 0 
            for rew in reversed(ep_rews):
                discounted_reward = rew + discounted_reward * self.gamma
                batch_rtgs.insert(0, discounted_reward)

        batch_rtgs = torch.tensor(batch_rtgs, dtype=torch.float)
        return batch_rtgs

    def rollout(self):
        batch_obs = []             
        batch_acts = []            
        batch_log_probs = []       
        batch_rews = []            
        batch_rtgs = []           
        batch_lens = []

        ts_done = 0
        while ts_done < self.timestamps_per_batch:
            ep_rews = []

            obs, _ = self.env.reset()
            done = False

            torch.tensor(obs)

            for ep_ts in range(self.max_timestamps_per_episode):
                ts_done += 1

                batch_obs.append(obs)

                action, log_prob = self.get_action(obs)
                obs, rew, done, _, _ = self.env.step(action)

                ep_rews.append(rew)
                batch_acts.append(action)
                batch_log_probs.append(log_prob)

                if done:
                    break
            
            batch_lens.append(ep_ts + 1)
            batch_rews.append(ep_rews)

        batch_obs = torch.tensor(batch_obs, dtype=torch.float)
        batch_acts = torch.tensor(batch_acts, dtype=torch.float)
        batch_log_probs = torch.tensor(batch_log_probs, dtype=torch.float)

        batch_rtgs = self.compute_rtgs(batch_rews)

        return batch_obs, batch_acts, batch_log_probs, batch_rtgs, batch_lens


    def evaluate(self, batch_obs, batch_acts):
        V = self.critic(batch_obs).squeeze()

        mean = self.actor(batch_obs)
        dist = MultivariateNormal(mean, self.cov_mat)
        log_probs = dist.log_prob(batch_acts)
        
        return V, log_probs

    def learn(self, max_iter):
        i = 0
        while i < max_iter:
            batch_obs, batch_acts, batch_log_probs, batch_rtgs, batch_lens = self.rollout()
            i += np.sum(batch_lens)

            V, _ = self.evaluate(batch_obs, batch_acts)

            A_i = batch_rtgs - V.detach()
            A_i = (A_i - A_i.mean()) / (A_i.std() + 1e-10) #Normalize
    
            for _ in range(self.updates_per_itter):
                V, current_log_probs = self.evaluate(batch_obs, batch_acts)
                ratios = torch.exp(current_log_probs - batch_log_probs)

                surr1 = ratios * A_i
                surr2 = torch.clamp(ratios, 1 - self.clip, 1 + self.clip) * A_i
                actor_loss = (-torch.min(surr1, surr2)).mean()
                critic_loss = nn.MSELoss()(V, batch_rtgs)

                self.actor_optimizer.zero_grad()
                actor_loss.backward(retain_graph = True)
                self.actor_optimizer.step()

                self.critic_optimzer.zero_grad()
                critic_loss.backward()
                self.critic_optimzer.step()

if __name__ == "__main__":
    #test on gymnasium env
    import gym
    env = gym.make('Pendulum-v1')
    model = PPO(env)
    model.learn(10000)