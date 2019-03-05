# coding: utf-8
import sys

import gym
import numpy as np
import gym.spaces


class BOSS():
#�s���̎��
#        ��Ұ��(�񕜗�)  ����MP  
#0:�����           40,      25
#1:�U��             10,       0
    HP_MAX = 200.
    MP_MAX = 100.
    def __init__(self):
         self.hp = self.HP_MAX
         self.mp = self.MP_MAX
    def select_action(self):
         if self.mp >= 25.:
             return 0 #0:�����
         else:
             return 1 #1:�U��  

class HERO():
#�s���̎��
#        ��Ұ��(�񕜗�)  ����MP  
#0:����             20,      10
#1:��            -50,       5
#2:�U��             10,       0
    HP_MAX = 100.
    MP_MAX = 100.
    def __init__(self):
         self.hp = self.HP_MAX
         self.mp = self.MP_MAX

class battle(gym.Env):
    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range ��ݒ肷��
        self.action_space = gym.spaces.Discrete(3)  # Hero�̍s���̐�
        self.observation_space = gym.spaces.Box(    
            low = 0.,          # �ŏ��l
            high = 100.,       # �ő�l
            shape=(2,)         # �ϑ��l -> ( ������HP, MP, )
        )
        self.reward_range = [-500., 500.] # WIN or LOSE
        self._reset()

    def _reset(self):
        # ���X�̕ϐ�������������
        self.HERO = HERO()
        self.BOSS = BOSS()
        self.done = False
        self.steps = 0
        return self._observe()

    def _step(self, action):
        # 1�X�e�b�v�i�߂鏈�����L�q�B�߂�l�� observation, reward, done(�Q�[���I��������), info(�ǉ��̏��̎���)
        boss_action = self.BOSS.select_action()
        # �@�G�̍s��
        if boss_action == 0:   # �����
            if self.BOSS.mp >= 25.:
                self.BOSS.mp -= 25.
                self.HERO.hp -= 40.
        elif boss_action == 1: # �U��
            self.HERO.hp -= 10.
        
        # �A�����̍s��
        if self.HERO.hp > 0:            # �����Ă�΍s���\
            if action == 0:        # ����
                if self.HERO.mp >= 10.:
                    self.BOSS.hp -= 20.
                    self.HERO.mp -= 10.
            elif action == 1:      # ��
                if self.HERO.mp >= 5.:
                    if self.HERO.hp < self.HERO.HP_MAX:
                        self.HERO.hp += 50.
                        self.HERO.mp -= 5.
            elif action == 2:      # �U��
                self.BOSS.hp -= 10.

        # �B�^�[������i�߂�
        self.steps += 1

        # �Chp����
        if self.BOSS.hp < 0:
            self.BOSS.hp = 0
        if self.HERO.hp < 0:
            self.HERO.hp = 0
        elif self.HERO.hp > self.HERO.HP_MAX:  # �񕜂������Ă����ꍇ�ɒ���
            self.HERO.hp = self.HERO.HP_MAX
        
        observation = self._observe()
        reward = self._get_reward()
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human �̏ꍇ�̓R���\�[���ɏo�́Bansi�̏ꍇ�� StringIO ��Ԃ�
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile.write( "HERO hp:"+str(self.HERO.hp)+",\tmp:"+ str(self.HERO.mp) + "\tBOSS hp:"+ str(self.BOSS.hp) +",\ mpt"+ str(self.BOSS.mp) +'\n')
        return outfile

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self):
        # ��V��Ԃ��B��V�̗^������������A�����ł�
        # - HERO�����񂾂�   (-50 + �^�����_���[�W/10) pt
        # - HERO�������Ă���  +0pt
        # - ��+������|������ +(50 - ���������^�[����) * 5) pt
        # �Ƃ���
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
