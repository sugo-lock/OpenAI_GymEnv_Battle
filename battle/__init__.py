from gym.envs.registration import register

register(
    id='battle-v0',
    entry_point='battle.env:battle'
)