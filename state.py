###=================================================
# This file creates a list for initial and final states from the text files.
########### Ex: [block_object_A, block_object_B, block_object_C,....]
# It then has a display function to display the state on screen.
# This file can also find a specific block for us
########### Ex: find([block_object_A, block_object_B, block_object_C,....], "A")
###=================================================

from scene import Scene
from block import Block
import copy


class State:

    def __init__(self):
        self.blocks = []
        
    def __eq__(self, other):
        for block1 in self.blocks:
            for block2 in other.blocks:
                if block1 == block2 and block1.on != block2.on:
                    return False
        return True   

    def copy(self):
        new_state = State()
        new_state.blocks = copy.deepcopy(self.blocks)
        # for block in self.blocks:
        #     new_state.blocks.append(block.copy)
        return new_state
    
    @staticmethod
    def find(state, id):
        """
        find the block.Block object based on ID
        :param state: list of blocks
        :param id: Name of the block
        :return: block.Block object if it exists
                 else None
        """
        for block in state:
            if block.id == id:
                return block
        return None
        #return next((item for item in state if item.id == id), None)

    def format_args(expr):
        i_open = expr.find('(')
        i_close = expr.find(')')

        arguments = expr[i_open + 1: i_close].replace(' ', '').split(',')

        args = [f'"{arg}"' for arg in arguments]
        args = "(" + ",".join(args) + ")"

        return f"{expr[:i_open]}{args}"

        #print(expr[i_open + 1: i_close].replace(' ', '').split(','))
        #print("")

    @staticmethod
    def display(blocks, message=""):
        print ("\n")
        print("******************")
        print(message)
        print("******************")
        print((str(Scene(blocks))))

    def square(self, id):
        # check if id exists in blocks
        if not id in self.blocks:
            block = Block(Block.SQUARE, id)
            self.blocks.append(block)

    def triangle(self, id):
        # check if id exists in blocks
        if not id in self.blocks:
            block = Block(Block.TRIANGLE, id)
            self.blocks.append(block)

    def on(self, id1, id2):
        try:
            # retrieve id
            block = self.find(self.blocks, id1)

            # retrieve table
            onto_block = self.find(self.blocks, id2)

            if block:
                block.place(onto_block)
            else:
                print (f"Blocks {id1, id2} are not defined")

        except TypeError:
            raise ValueError(f"There is a problem with the state on{id1, id2}")


    def create_state_from_file(self, filename="input.txt"):

        table = Block(Block.TABLE, "table")
        self.blocks.append(table)

        for line in open(filename).readlines():
            line = line.strip()
            if line:
                line = State.format_args(line)
                exec(f"self.{line}")

        return self.blocks


    def is_on_table(self, id):
        block = self.find(self.blocks, id)

        table_block = self.find(self.blocks, "table")

        if block.on == table_block:
            return True
        return False
    
    def get_blocks_on_table(self):
        blocks_on_table = []
        blocks_not_on_table = []
        for block in self.blocks:
            if(self.is_on_table(block.id)):
                blocks_on_table.append(block)
            else:
                blocks_not_on_table.append(block)
        return blocks_on_table,blocks_not_on_table

    #This is a helper function for the heuristic_evaluation method. This will compute the number of correct 
    #on relations for stacks that are correct from the table up. 
    def heuristic_helper(self, table_overlap, current_not_table, goal_not_table):
        new_overlap = []       #List for the blocks that are on one of the blocks in overlap
        sum = 0                #Integer value for the number of correct relations
        
        #This section will find the blocks that are in both 
        for block_current in current_not_table:
            for block_goal in goal_not_table:
                if block_current == block_goal: #Same block
                    if block_current.on in table_overlap and block_goal.on == block_current.on: #If the block is on the same block in the current and goal states
                        sum += 1
                        new_overlap.append(block_current)
                        current_not_table.remove(block_current)
                        goal_not_table.remove(block_current)
        if current_not_table and new_overlap:
            return sum + self.heuristic_helper(new_overlap, current_not_table, goal_not_table)
        else:
            return sum

    def heuristic(self, current_state, goal_state):
        overlap = []    #The overlap between blocks that are on the table in both the current and goal states
        sum = 0         #The number of relations that are correct from the table up
        
        current_table, current_not_table = current_state.get_blocks_on_table()
        goal_table, goal_not_table = goal_state.get_blocks_on_table()
        
        for block in current_state.blocks:
            if block.air:
                sum += 0.01
        
        #This section will check if all of the blocks on the table in the current state are also on the table in the goal state
        for block in current_table:     
            if block in goal_table:
                sum += 1
                overlap.append(block)
                
        #This helper function will add to sum the number of correct relations that are on the overlap of blocks
        sum += self.heuristic_helper(overlap, current_not_table, goal_not_table)    
        return sum
    