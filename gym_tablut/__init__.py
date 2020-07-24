from gym.envs.registration import register

register(
    id='Tablut-v0',
    entry_point='gym_tablut.envs:TablutEnv',
)