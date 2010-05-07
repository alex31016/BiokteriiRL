QNodeDict={}

class QNode():
    def __init__(self, state, action_dict = None):
        self.state = state #State string, like AT for Alto,True
        self.action_dict = action_dict

class QAction():
    def __init__(self,action_name, source_node, destination_node,  reinforcement = 0):
        self.name = action_name
        self.source = source_node
        self.destination= destination_node #QNodeList
        self.reinforcement = reinforcement
    
class Table():
    def __init__(self, q_action_dict):
        self.actions= q_action_dict

    def __getitem__(self,key):
        return self.actions[key]

    def read_from_file(self, fileName):
        actionDict = {}
        file = open(filename, "r")
        for line in file:
            info=line.split(",")
            SourceName=info[0][0]+info[1][0]
            if QNodeDict.has_key(SourceName):
                QNodeSource=QNodeDict[SourceName]
            else:
                QNodeDict.update({SourceName:Node(SourceName)})
                QNodeSource=Node(SourceName)
            DestName=info[2][0]+info[3][0]
            if QNodeDict.has_key(DestName):
                QNodeSource=QNodeDict[DestName]
            else:
                QNodeDict.update({DestName:Node(DestName)})
                QNodeSource=Node(DestName)
            reinforcement=int(line[5])
            action = QAction(ActionName,QNodeSource, QNodeDestination, reinforcement)
            actionDict.update({SourceName+DestName:action})
        return None

import random
class QAgent():
    def __init__(self, r_table, q_table, start_node, learning_rate=0.5):
        self.r_table = r_table
        self.q_table = q_table
        self.current_node = start_node
        self.learning_rate = learning_rate
        self.selection_policy = "random"
        
    def _select_state(self):
        if self.selection_policy=="random":
            self.current_node = random.choice(self.current_node.action_dict.values())
        if self.selection_policy == "bestchoice":
            self.current_node = self._get_max_action().destination

    def _update_q_table(self):
        node_state = self.current_node.state

        self.q_table[node_state].reinforcement = (self.r_table[node_state].reinforcement +
                                                 (self.learning_rate * self._get_max_action().reinforcement)
                                                 )

    def _get_max_action(self):
        max = -1000
        max_action = None
        q_action_dict = self.q_table[self.current_node.state]
        for action_key in q_action_dict:
            action = q_action_dict[action_key]
            r = action.reinforcement            
            if r > max:
                max = r
                max_action = action

        return max_action

    def update(self):
        if not self.q_table[self.current_node.state].action_dict.items()==None:
            self._select_state()
            self._update_q_table()
            return True
        else:
            #Es estado final
            print "estado final"
            return False
