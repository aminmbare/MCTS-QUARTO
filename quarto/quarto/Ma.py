import time 
from quarto import Quarto, Player
from copy import deepcopy
from math import sqrt, log
import numpy as np
import logging

import random
C = sqrt(2)

class RandomPlayer(Player):
    """Random player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)
def get_available_pieces(state:Quarto)->set:
    pieces = set(range(16))
    pieces_on_board = set()
    for row in state.get_board_status(): 
        for element in row : 
            if element != -1 : 
                pieces_on_board.add(element)
    return pieces - pieces_on_board

def get_available_positions(state: Quarto)->list: 
    moves = list()
    for i, row in enumerate(state.get_board_status()): 
        for j,element in enumerate(row): 
            if element == -1 : 
                moves.append((i,j))     
    return moves            
class Node: 
    def __init__(self,move,parent, phase : bool, player : bool):
        self.move = move 
        self.parent = parent 
        self.N = 0 
        self.Q = 0 
        self.children = dict()
        self.outcome = -1
        self.phase = phase
        self.player = player 
        
    def add_children(self, children :list)-> None: 
        for child in children : 
            self.children[child.move] = child
            
    def value(self) -> float : 
        if self.N == 0 :
            return 1000000
        else : 
            return self.Q /self.N + C * sqrt(log(self.parent.N/self.N))
        
        
        
class MCTS(Player):
    def __init__(self,quarto):
        self.root_state  = quarto
        self.root = Node(None ,None,None ,True )

        self.node_count = 0 
        self.num_rollouts = 0 
        self.time_limit = 5
    def select_node(self,state : Quarto,phase : bool , player : bool) -> tuple:
        node = self.root
        CurrState = deepcopy(state)

        while len(node.children) != 0:
            children = node.children.values()
            max_value = max(children, key=lambda n: n.value()).value()
            max_nodes = [n for n in children if n.value() == max_value]

            node = random.choice(max_nodes)
            player = node.player
            new_phase = node.phase
            #print(type(node.move))
            if type(node.move) is tuple:
                CurrState.place(*node.move)
            else : 
                CurrState.select(node.move)
            if node.N == 0:
                #new_player , new_phase =self.get_player_and_phase(player , phase )
                return node, CurrState, new_phase
            player , phase =self.get_player_and_phase(player , new_phase )
            #new_player , new_phase =self.get_player_and_phase(player , phase )
        if self.expand(node, state,phase,player):
            node = random.choice(list(node.children.values()))
            if type(node.move) is tuple:
                CurrState.place(*node.move)
            else: 
                CurrState.select(node.move)
        new_player , new_phase =self.get_player_and_phase(player , phase )

        return node, CurrState,new_phase
    @staticmethod
    def get_player_and_phase(player , phase)-> tuple:
        return player ^ phase ,not  phase 
    
    def best_move(self): 
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        best_child = random.choice(max_nodes)
        return best_child.move
    
    
    def expand(self, parent: Node, state: Quarto,phase : bool , player : bool) -> bool:
        if state.check_finished():
            return False
        if phase :
            children = [Node(move, parent,phase, player) for move in get_available_pieces(state)]
        else : 
            children = [Node(move, parent,phase, player) for move in get_available_positions(state)]
        parent.add_children(children)

        return True
    
    
    def back_propagate(self, node: Node, turn: int, outcome: int) -> None:

        # For the current player, not the next player
        #reward = 0 if outcome == turn else 1

        while node is not None:
            node.N += 1
            if outcome == 0 and node.player == turn : 
                node.Q += 1
            node = node.parent
            #if outcome == -1:
            #    reward = 0
            #else:
            #    reward = 1 - reward
    
    
    
    def search(self,state: Quarto, phase : bool,player : True): 
        start_time = time.process_time()
        random_player = RandomPlayer
        num_rollouts = 0
        while time.process_time() - start_time < self.time_limit:
            node, new_state , new_phase = self.select_node(state,phase,player)
            if new_phase :
                outcome = self.roll_out_choose_piece(new_state,RandomPlayer)
            else : 
                outcome = self.roll_out_place_piece(new_state,RandomPlayer)
            self.back_propagate(node, node.player, outcome)
            num_rollouts += 1
        run_time = time.process_time() - start_time
        self.run_time = run_time
        self.num_rollouts = num_rollouts

    def best_move(self,state : Quarto):
        if state.check_finished():
            return -1

        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        best_child = random.choice(max_nodes)

        return best_child.move
    
    def choose_piece(self)-> int:
        self.time_limit = 15
        phase = True 
        state = deepcopy(self.root_state)
        self.search(state,phase,True)
        move =self.best_move(state)
        self.root = Node(None ,None,None ,True)
        print(f" time : {self.run_time}, roll outs : {self.num_rollouts}")

        return move
    
    
    def place_piece(self)->tuple[int,int] : 
        self.time_limit = 30
        phase = False
        state = deepcopy(self.root_state)
        self.search(state,phase,True)
        move =self.best_move(state)
        self.root = Node(None ,None,None ,True)
        print(f" time : {self.run_time}, roll outs : {self.num_rollouts}")
        #if self.time_limit < 20:
        #    self.time_limit+=2 
        return move
    
    
    def roll_out_choose_piece(self,state:Quarto, Random_player : classmethod)-> int : 
        player = Random_player(state)
        winner = -1
        turn = 0
        if state.check_finished(): 
            return 1- turn 
        while winner < 0 and  not state.check_finished():
            piece_ok = False
            while not piece_ok:
                piece_ok = state.select(player.choose_piece())
            piece_ok = False
            turn =  1 - turn 
            while not piece_ok:
                x, y = player.place_piece()
                piece_ok = state.place(x, y)
            winner = state.check_winner()
            if winner != -1 : 
                winner = turn 
                break     

        return winner
        
    
    
    def roll_out_place_piece(self,state:Quarto, Random_player : classmethod)-> int : 
        player = Random_player(state)
        winner = -1
        turn = 0
      
        while winner < 0 and  not state.check_finished():
            piece_ok = False
          
            while not piece_ok:
                x, y = player.place_piece()
                piece_ok = state.place(x, y)
            winner = state.check_winner() 
            if winner != -1 :                  
                winner = turn  
                break     
            if not state.check_finished():
                break 
            piece_ok = False
            while not piece_ok:
                piece_ok = state.select(player.choose_piece())
            winner = turn
            turn = 1 - turn 

        return winner

        
    
        