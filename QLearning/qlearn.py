import random
class QAction():
    def __init__(self,action_name, source_node,
                 destination_node,  reinforcement = 0):
        self.name = action_name
        self.source = source_node
        self.destination= destination_node 
        self.reinforcement = reinforcement

class Table():
    def __init__(self, q_action_dict=None):
        if q_action_dict == None:
            self.actions_for_state = self.read_from_file('rtable.csv')
        else:
            self.actions_for_state= q_action_dict


    def __getitem__(self,key):
        return self.actions_for_state[key]

    def print_table(self):
        print "--"*20
        dict = action_dict
        for k in dict:
            for entry in dict[k]:
                act = dict[k][entry]
                print act.name, act.source, act.destination, act.reinforcement
        print "--"*20

    def read_from_file(self, filename):
        action_dict= {}
        file = open(filename, "r")

        for line in file:
            data=line.split(",")
            source_state_name= data[0]
            action_name= data[1]
            destination_state_name= data[2]
            reinforcement = int(data[3])
            print "from %s to %s with reinforcement %d (%s)"%(source_state_name, destination_state_name, reinforcement, action_name)

            r_action = QAction(action_name, source_state_name,
                               destination_state_name, reinforcement)
            if not action_dict.has_key(source_state_name):
                action_entry = {action_name: r_action}
                action_dict.update({source_state_name:action_entry})
            else:
                action_dict[source_state_name].update(
                                                     {action_name:r_action}
                                                     )

        print "--"*20
        dict = action_dict
        for k in dict:
            for entry in dict[k]:
                act = dict[k][entry]
                print act.name, act.source, act.destination, act.reinforcement
        print "--"*20
        return Table(action_dict)

    def copy(self):
        return self.actions_for_state.copy()

class QAgent():
    def __init__(self, r_table, start_state, learning_rate=0.3):
        self.r_table = r_table
        self.q_table = self._create_q_table()
        self.current_state = start_state
        self.learning_rate = learning_rate
        self.selection_policy = "random"
        self.action_map = {"A":[self._get_attack_action, self._get_eat_action],
                           "M":[self._get_eat_action, self._get_defend_action],
                           "B":[self._get_eat_action, self._get_defend_action],
                           "X":[]}


#    def _create_q_table(self):
#        q_table = self.r_table.copy() #hard copy (by value)
#
#        for state in q_table:
#            action_entry_dict = q_table[state]
#            for action_key in action_entry_dict:
#                action_entry_dict[action_key].reinforcement = 0
#        return Table(q_table)


    def _create_q_table(self):
        dict = {}
        r_table = self.r_table.copy()
        for state_key in r_table:
            action_dict = r_table[state_key]
            for action_key in action_dict:
                action = action_dict[action_key]
                q_action = QAction(action.name, action.source, action.destination, action.reinforcement)
                if not dict.has_key(state_key):
                    dict[state_key]={}
                dict[state_key].update({action_key:q_action})
        return Table(dict)


    def _get_max_action(self, cell):        
        max = -1000
        max_action = None
        color_code = self._get_cell_color(cell)
        action_list = ["A"+color_code, "C"+color_code,"D"+color_code]
        for action in action_list:
            action_dict = self.q_table[self.current_state]
            if not action_dict.has_key(action):
                continue
            q_action = action_dict[action]
            r = q_action.reinforcement
            if r > max:
                max = r
                max_action = q_action
        return max_action


    def _select_state(self, cell):
        action = None
        if self.selection_policy=="random":
            action = random.choice(self.action_map[self.current_state])(cell)
        if self.selection_policy == "optimal":
            action = self._get_max_action(cell)

        if action == None:
            print ("No existing selection policy"
                  "(%s) selected") %(self.selection_policy)
            return None

        print "Moved from %s to %s with action %s"%(self.current_state,action.destination, action.name)
        self.current_state = action.destination
        return action
                        

    def _update_q_table(self, action, cell):
        node_state = action.source#self.current_state
        self.q_table[node_state][action.name].reinforcement= self.r_table[node_state][action.name].reinforcement +(self.learning_rate * (self._get_max_action(cell).reinforcement))
        print "r_table reinforcement: %f" %(self.r_table[node_state][action.name].reinforcement)
        print "Updated q_table[%s][%s] to %f" %(node_state,action.name,self.q_table[node_state][action.name].reinforcement)

    def _update_selection_policy(self):
        actions_learned = 0
        total_actions = 0
        action_dict = self.q_table.actions_for_state
        for state in action_dict:
            action_entry_dict = action_dict[state]
            total_actions += len(action_entry_dict)
            for action_key in action_entry_dict:
                if action_entry_dict[action_key].reinforcement != 0:
                    actions_learned+= 1
        mark = float(actions_learned) / float(total_actions)
        throw = random.random()
        if throw <=mark:
            self.selection_policy="optimal"
        else:
            self.selection_policy="random"
        print "Mark: %f, throw: %f -> %s (learned:%d,total:%d)"%(mark,throw,self.selection_policy, actions_learned, total_actions)


    def update(self, cell):
        if self.action_map[self.current_state]:
            action = self._select_state(cell)
            if self.current_state != "X":
                self._update_q_table(action, cell)
                self._update_selection_policy()
                return action.name[0]
            else:
                print "estado final A"
                return "X"
                #return action.name[0]
        else:
            print "estado final"
            return "X"


    def _normalize_color(self, color_str):
        if color_str == "Red":
            return "R"
        if color_str == "Green":
            return "V"
        if color_str == "Blue":
            return "A"


    def _get_cell_color(self,cell):
        cell_color_name = cell.outerColor
        return self._normalize_color(cell_color_name)


    def _get_action(self,table,action, state = None):
        if state==None:
            state = self.current_state
        action = table[state][action]
        return action


    def _get_attack_action(self,cell):
        action = "A"+self._get_cell_color(cell)
        return self._get_action(self.q_table,action)


    def _get_eat_action(self,cell):
        action = "C"+self._get_cell_color(cell)
        return self._get_action(self.q_table,action)


    def _get_defend_action(self,cell):
        action = "D"+self._get_cell_color(cell)
        return self._get_action(self.q_table,action)


class Cell:
    def __init__(self):
        self.outerColor ="Red"

def main():
    rtable = Table()
    vir = QAgent(rtable,'A')
    c= Cell()
    c.outerColor='Red' #random.choice(['Red','Blue','Green'])
    while True:        
        input = raw_input("\n")
        if input == "print":
            vir.q_table.print_table()
        if input == "restart":
            vir.current_state="A"
            vir.update(c)
            continue
        if input:
            c.outerColor = input
        vir.update(c)

if __name__ == '__main__':
    main()

#Dar refuerzo negativo cuando se dfiende de comida, pero no matarlo B - DA
