# coding: utf-8
import sys

import gym
import numpy as np
import gym.spaces


class BOSS():
#行動の種類
#        ﾀﾞﾒｰｼﾞ(回復量)  消費MP  
#0:大呪文           40,      25
#1:攻撃             10,       0
    HP_MAX = 200.
    MP_MAX = 100.
    def __init__(self):
         self.hp = self.HP_MAX
         self.mp = self.MP_MAX
    def select_action(self):
         if self.mp >= 25.:
             return 0 #0:大呪文
         else:
             return 1 #1:攻撃  

class HERO():
#行動の種類
#        ﾀﾞﾒｰｼﾞ(回復量)  消費MP  
#0:呪文             20,      10
#1:回復            -50,       5
#2:攻撃             10,       0
    HP_MAX = 100.
    MP_MAX = 100.
    def __init__(self):
         self.hp = self.HP_MAX
         self.mp = self.MP_MAX

class battle(gym.Env):
    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range を設定する
        self.action_space = gym.spaces.Discrete(3)  # Heroの行動の数
        self.observation_space = gym.spaces.Box(    
            low = 0.,          # 最小値
            high = 100.,       # 最大値
            shape=(2,)         # 観測値 -> ( 自分のHP, MP, )
        )
        self.reward_range = [-500., 500.] # WIN or LOSE
        self._reset()

    def _reset(self):
        # 諸々の変数を初期化する
        self.HERO = HERO()
        self.BOSS = BOSS()
        self.done = False
        self.steps = 0
        return self._observe()

    def _step(self, action):
        # 1ステップ進める処理を記述。戻り値は observation, reward, done(ゲーム終了したか), info(追加の情報の辞書)
        boss_action = self.BOSS.select_action()
        # ①敵の行動
        if boss_action == 0:   # 大呪文
            if self.BOSS.mp >= 25.:
                self.BOSS.mp -= 25.
                self.HERO.hp -= 40.
        elif boss_action == 1: # 攻撃
            self.HERO.hp -= 10.
        
        # ②自分の行動
        if self.HERO.hp > 0:            # 生きてれば行動可能
            if action == 0:        # 呪文
                if self.HERO.mp >= 10.:
                    self.BOSS.hp -= 20.
                    self.HERO.mp -= 10.
            elif action == 1:      # 回復
                if self.HERO.mp >= 5.:
                    if self.HERO.hp < self.HERO.HP_MAX:
                        self.HERO.hp += 50.
                        self.HERO.mp -= 5.
            elif action == 2:      # 攻撃
                self.BOSS.hp -= 10.

        # ③ターン数を進める
        self.steps += 1

        # ④hp調整
        if self.BOSS.hp < 0:
            self.BOSS.hp = 0
        if self.HERO.hp < 0:
            self.HERO.hp = 0
        elif self.HERO.hp > self.HERO.HP_MAX:  # 回復しすぎていた場合に調整
            self.HERO.hp = self.HERO.HP_MAX
        
        observation = self._observe()
        reward = self._get_reward()
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human の場合はコンソールに出力。ansiの場合は StringIO を返す
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile.write( "HERO hp:"+str(self.HERO.hp)+",\tmp:"+ str(self.HERO.mp) + "\tBOSS hp:"+ str(self.BOSS.hp) +",\ mpt"+ str(self.BOSS.mp) +'\n')
        return outfile

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self):
        # 報酬を返す。報酬の与え方が難しいが、ここでは
        # - HEROが死んだら   (-50 + 与えたダメージ/10) pt
        # - HEROが生きてたら  +0pt
        # - ↑+魔王を倒したら +(50 - かかったターン数) * 5) pt
        # とした
        if self.HERO.hp <= 0.:
            return -100. + ( self.BOSS.HP_MAX - self.BOSS.hp )/10
        else:
            if self.BOSS.hp <= 0.:
                return (50. - self.steps) * 5
            else:
                return 0.

    def _observe(self):
        observation = np.array([self.HERO.hp, self.HERO.mp],)
        return observation

    def _is_done(self):
        if ( (self.HERO.hp <= 0.) | (self.BOSS.hp <= 0.) ):
            return True
        else:
            return False
