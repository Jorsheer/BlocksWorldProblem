###=================================================
# This file is where you need to create a plan to reach the goal state from the initial state
# This file must accept any combination of with the given blocks: A, B, C, D, E
# This file should also reach the final state of any combination with the blocks above
# It must also display all intermediate states
###=================================================

from state import State
from block import Block
class Plan:

    def __init__(self, initial_state, goal_state):
        """
        Initialize initial state and goal state
        :param initial_state: list of blocks in the initial state
        :type initial_state: list of block.Block objects
        :param goal_state: list of blocks in the goal state
        :type initial_state: list of block.Block objects
        """
        self.initial_state = initial_state
        self.goal_state = goal_state

    #***=========================================
    # First implement all the operators
    # I implemented two operators to give you guys an example
    # Please implement the remainder of the operators
    #***=========================================

    def putdown(self, block1):
        """
        Operator to put the block on the table
        :param block1: block1 to put on the table
        :type block1: Object of block.Block
        :return: None
        """

        # get table object from initial state
        table = State.find(self.initial_state, "table")

        if block1.air:
            block1.on = table
            block1.clear = True
            block1.air = False
            
    def pick_up(self, block1):
        """
        Operator to pick a block up off the table
        :param block1: block1 to pick up off the table
        :type block1: Object of block.Block
        :return: None
        """
        table = State.find(self.initial_state, "table")
        
        if block1.clear and block1.on == table:
            block1.clear = False
            block1.air = True
            block1.on = None
            

    def unstack(self, block1, block2):
        """
        Operator to unstack block1 from block 2

        :param block1: block1 to unstack from block2
        :type block1: Object of block.Block
        :type block2: Object of block.Block
        :return: None
        """

        # if block1 is clear safe to unstack
        if block1.clear:

            # block1 should be in air
            # block1 should not be on block2
            # set block2 to clear (because block1 is in air)
            block1.clear = False
            block1.air = True
            block1.on = None

            block2.clear = True

    def stack(self, block1, block2):
        """
        Operator to stack block1 on block2

        :param block1: block1 to stack on block2
        :type block1: object of block.Block
        :type block2: object of block.Block
        :return: none
        """
        #block1 should be in the air
        if block1.air and block2.clear:
            #block 1 is no longer in the air
            #block 2 is no longer clear
            #block 1 needs to be cleared
            block1.on = block2
            block1.air = False
            block2.clear = False
            block1.clear = True

    # ***=========================================
    # After you implement all the operators
    # The next step is to implement the actual plan.
    # Please fill in the sample plan to output the appropriate steps to reach the goal
    # ***=========================================
    

    def gbfs(self, initial_state, goal_state):
        current_state = State()
        current_state = initial_state #make the current state the starting state
        successors = [] #view all the possible moves that could be made
        actions = [] #All actions that correspond to the successors
        visited = [] #used to not have the same states repeated over and over again
        while current_state != goal_state: #if current_state = goal_state, the search is over
            successors, actions = self.generate_successors(current_state) #set successors to all moves
            #print(successors)
            best_heuristic = 0
            index = 0
            for state in successors: #search moves
                if state.heuristic(state, goal_state) > best_heuristic: #if the heuristic is best, switch to that
                    if not state in visited: #make sure we haven't seen this before
                        current_state = state #make the current state this state
                        best_heuristic = state.heuristic(current_state, goal_state) #modify best heuristic
                        index = successors.index(state)
            State.display(current_state.blocks, message=actions[index])
            #print("heuristic is ")
            #print(best_heuristic)
        print("Goal reached")
            
    def generate_successors(self, state):
        """
        Generate possible successor states from the current state
        :param state: Current state
        :type state: list of block.Block objects
        :return: List of successor states and list of actions corresponding to the successor states
        :rtype: list of list of block.Block objects and list of strings
        """
        successors = []
        actions = []
        for block in state.blocks:
            if block.type != Block.TABLE and (block.isclear or block.air):  #check if block is not on table and is clear
                
                #If the block is in the air, it can be put on the table or on another block.
                if block.air:
                    #Section to put the block on the table
                    new_state = state.copy() #create copy of current state
                    new_block = State.find(new_state.blocks, block.id) #Find the same block in the new state
                    self.putdown(new_block) #Put the block down in the new state
                    successors.append(new_state) #Append the new state to successors
                    actions.append(f"Put-down({new_block})") #Append the action to actions
                    
                    #Section to stack the block
                    #block2 is all the blocks in state that can have another block stacked on it
                    for block2 in state.blocks: 
                        if block2.isclear: 
                            new_state = state.copy() #create copy of current state
                            
                            block_to_stack = State.find(new_state.blocks, block.id) #Find the block that is being stacked in the new state
                            receiving_block = State.find(new_state.blocks, block2.id) #Find the block that is having a block stacked on it in the new state
                            
                            self.stack(block_to_stack, receiving_block) #Stack the block 
                            successors.append(new_state) #Append the new state to successors
                            actions.append(f"Stack{block_to_stack, receiving_block}") #append the action to actions
                
                #If the block is on the table, it can be picked up
                elif state.is_on_table(block.id): 
                    new_state = state.copy() #create copy of current state
                    
                    block_to_pickup = State.find(new_state.blocks, block.id) #Find the block to be picked up in new_state
                    self.pick_up(block_to_pickup) #Pick up the block
                    successors.append(new_state) #Append the new state to successors
                    actions.append(f"Pick-up({block_to_pickup})") #append the action to actions
                    
                #If block is on another block, it can be unstacked
                else:  
                    for block2 in state.blocks:
                        if block2 == block.on:  #find the block that the current block is on
                            new_state = state.copy() #create copy of current state
                            
                            new_block1 = State.find(new_state.blocks, block.id)
                            new_block2 = State.find(new_state.blocks, block2.id)
                            
                            self.unstack(new_block1, new_block2) #Unstack 
                            successors.append(new_state) #Append the new state to successors
                            actions.append(f"Unstack{new_block1, new_block2}") #append the action to actions
                            
        return successors, actions
            
    def sample_plan(self):

        # get the specific block objects
        # Then, write code to understand the block i.e., if it is clear (or) on table, etc.
        # Then, write code to perform actions using the operators (pick-up, stack, unstack).

        # Below I manually hardcoded the plan for the current initial and goal state
        # You must automate this code such that it would produce a plan for any initial and goal states.

        block_c = State.find(self.initial_state, "C")
        block_d = State.find(self.initial_state, "D")

        # Unstack the block
        self.unstack(block_d, block_c)

        # print the state
        action = f"unstack{block_d, block_c}"
        State.display(self.initial_state, message=action)

        # put the block on the table
        self.putdown(block_d)

        # print the state
        action = f"Putdown({block_d}, table)"
        State.display(self.initial_state, message=action)



if __name__ == "__main__":

    print("test")
    # get the initial state
    initial_state = State()
    initial_state_blocks = initial_state.create_state_from_file("input.txt")
    #display initial state
    State.display(initial_state_blocks, message="Initial State")

    # get the goal state
    goal_state = State()
    goal_state_blocks = goal_state.create_state_from_file("goal.txt")
    #print(goal_state_blocks)
    #display goal state
    State.display(goal_state_blocks, message="Goal State")

    #sample of how to call on table, initial state being what state it currently is, and "A" being the id of the block
    State.is_on_table(initial_state, "A")
    #sample of using get_blocks_on_table
    print("currently on table:")
    print(State.get_blocks_on_table(initial_state))
    """
    Sample Plan
    """

    #p = Plan(initial_state_blocks, goal_state_blocks)
    #p.sample_plan()

    new_plan = Plan(initial_state_blocks, goal_state_blocks)
    #succ, act = new_plan.generate_successors(initial_state)
    #print(act)
    
    new_plan.gbfs(initial_state, goal_state)