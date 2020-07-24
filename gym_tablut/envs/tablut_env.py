import gym
import numpy as np
from gym import spaces, logger
from gym.envs.classic_control import rendering
from gym.utils import seeding
from gym_tablut.envs._globals import *


class TablutEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        """
        Create the environment
        """
        self.action_space = None
        self.observation_space = None
        self.state = None
        self.done = False
        self.steps_beyond_done = None
        self.viewer = None
        self.np_random = seeding.np_random(0)

    def step(self, action: int, player: int):
        """
        Apply a single step in the environment using the given action

        :param action: The action to apply
        :param player: The playing actor
        """
        pass

    def reset(self):
        """
        Reset the current scene, computing the observations

        :return: The state observations
        """
        pass

    def render(self, mode='human'):
        """
        Render the current state of the scene

        :param mode: The rendering mode to use
        """
        if self.viewer is None:
            self.viewer = rendering.Viewer(SCREEN_WIDTH, SCREEN_HEIGHT)

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    def close(self):
        """
        Terminate the episode
        """
        if self.viewer:
            self.viewer.close()
            self.viewer = None
