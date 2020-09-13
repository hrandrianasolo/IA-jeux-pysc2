from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.lib import units

_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id

_X_COORD = features.FeatureUnit.x
_Y_COORD = features.FeatureUnit.y

#  python3 -m pysc2.bin.agent --map DefeatZerglingsAndBanelings --agent hrandrianasolo-s-v-1.SimpleAgent --max_episodes 10 --use_feature_units

class SimpleAgent(base_agent.BaseAgent):
    M = []

    def dist(self, xa, ya, xb, yb):
        return ((xb - xa)*(xb - xa)) + ((yb - ya)*(yb - ya))

    def set_marines_coord(self, obs):
        marines = [marine for marine in obs.observation.feature_units if marine.alliance == features.PlayerRelative.SELF]
        unitLiveCoord = []
        unitIdLiveAlreadySelected = []

        for i in range(len(marines)):
            isInM = -1 # -1 not in | 0 in but already selected | 1 in not selected yet
            unitId = 0
            mx = marines[i][_X_COORD]
            my = marines[i][_Y_COORD]

            for j in range(len(self.M)):
                Mx = self.M[j][1]
                My = self.M[j][2]

                if mx == Mx and my == My :                       
                    if  self.M[j][0] == 3 :
                        unitIdLiveAlreadySelected.append(j)
                        isInM = 0
                    else:
                        isInM = 1
                        unitId = j
                    break

            if isInM == 1 :
                unitLiveCoord.append(self.M[unitId])
            if isInM == -1 :
                unitLiveCoord.append([1, mx, my])
           
        for i in range(len(unitIdLiveAlreadySelected)):
            unitLiveCoord.append([1, self.M[i][1], self.M[i][2]])
        
        self.M.clear()
        self.M = unitLiveCoord

    def reset(self):
        self.M = []
        
    def closest_enemy_position(self, obs ,pos):
        enemys = [shard for shard in obs.observation.feature_units if shard.alliance == features.PlayerRelative.ENEMY]
        
        best_dist = 10000
        best_i = 0
        for i in range(len(enemys)):
            new_dist = self.dist(pos[0], pos[1], enemys[i][_X_COORD], enemys[i][_Y_COORD])
            if new_dist < best_dist:
                best_dist = new_dist
                best_i = i
        
        return [enemys[best_i][_X_COORD], enemys[best_i][_Y_COORD]]

    def step(self, obs):
        super(SimpleAgent, self).step(obs)
        self.set_marines_coord(obs)
        
        for i in range(len(self.M)):
            if self.M[i][0] == 1 :
                target = [self.M[i][1],self.M[i][2]]
                self.M[i][0] = 2
                return actions.FUNCTIONS.select_point("select", target)
 
            if _MOVE_SCREEN in obs.observation["available_actions"] and self.M[i][0] == 2:
                pos = [self.M[i][1], self.M[i][2]]
                target = self.closest_enemy_position(obs, pos)
                self.M[i][0] = 3
                return actions.FUNCTIONS.Move_screen("now", target)
            
        return actions.FUNCTIONS.no_op()
