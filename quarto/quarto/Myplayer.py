import time 
from quarto import Quarto, Player
from copy import deepcopy
from math import sqrt, log
import numpy as np
import logging
from main import RandomPlayer
import random


LOG = logging.getLogger(__name__)
C = sqrt(2)
    
def get_available_pieces(state:Quarto)->set:
    pieces = set(range(16))
    pieces_on_board = set()
    for row in state.get_board_status(): 
        for element in row : 
            if element != 0 : 
                pieces_on_board.add(element)
    return pieces - pieces_on_board

def get_available_positions(state: Quarto)->list: 
    moves = list()
    for i, row in enumerate(state.get_board_status()): 
        for j,element in enumerate(row): 
            if element == -1 : 
                moves.append((i,j))     
    return moves   

class RandomPlayer(Player):
    """Random player"""

    def __init__(self, quarto:Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self,available_pieces : list ) -> int:
        return random.choice(available_pieces)

    def place_piece(self,available_positions : list ) -> tuple[int, int]:
        return random.choice(available_positions)      

class Node: 
    ''' Two types of nodes 
     1 - selection nodes : { represent by the state (True for selection and false for placing), the player whether it's the minimizing ( False )or the maximizing ( True) player
     ,N and Q , its  the children nodes  } 2 - placing nodes : {represent by the state (True for selection and false for placing), the player whether it's the minimizing ( False )or the maximizing ( True) player
     ,N and Q , its  the children nodes}
    ## '''
    def __init__(self,state : Quarto, phase : bool , player_turn : bool,piece : int  ) -> None:
        self.state = state
        self.N = 0
        self.Q = 0 
        self.piece = piece ## if the action that takes to this node comes from selection phase 
        self.player_turn = player_turn
        if phase : 
            self.children={o :None for o in get_available_pieces(state) }
        else :
            self.children={o :None for o in get_available_positions(state) }    
        
    def __str__(self)-> str : 
        return  f"Node(state={self.state}, N={self.N}, Q={self.Q}, children={self.children})"
    
    
                                                
class MCTS(Player):
    def __init__(self,quarto ): 
        #super().__init__(quarto)
        self.quarto_state = quarto
        self.states_to_nodes = dict()
        self.history = set()
        self.time_limit = 10
        self.Node = Node
        #self.player = True ## True : player 1 , False : player 2
        #self.phase = True  ##  True : selection , False : placing

    @staticmethod
    def compute_ucb(w:int,n: int , N: int,player : bool)-> float : 
        if player :
          return w/n +C *sqrt(log(N)/n)
        else : 
            return 1-w/n

    def explore(self, state: Quarto,player: bool , phase : bool,piece : int): 
        
        LOG.debug(f"exploring from state {state}")      
        if state.check_finished(): 
            LOG.debug("game is over")
        #state = deepcopy(state)   
        ucb = dict()

        state_hash = self.hashing(state,player, phase,piece)
        self.history.add(state_hash)

        node = self.states_to_nodes[state_hash]
        CurrState = deepcopy(state)
        for move , game_hash in node.children.items(): 
            if game_hash is None : 
                LOG.debug(f"Unexplored node found for action {move}")
                if type(move) is tuple : 
                    CurrState.place(*move)
                else :   
                    CurrState.select(move)
                    piece = move 
                new_player, new_phase = self.get_player_and_phase(player, phase)
                new_hash = self.hashing(CurrState, new_player, new_phase,piece)
                node.children[move] = new_hash
                return CurrState,new_player ,new_phase , piece
            game_node = self.states_to_nodes[game_hash]
            w = game_node.Q
            n = game_node.N
            N = node.N
            turn = game_node.player_turn

            ucb[move] = self.compute_ucb(w,n,N,player)
            
        chosen_move = max(ucb,key = lambda k : ucb[k])
        if type(move) is tuple : 
            CurrState.place(*chosen_move)
        else : 
            CurrState.select(chosen_move)
            piece = chosen_move
        #node.children[chosen_move] = self.hashing(CurrState)
        #print(phase , piece,player , state.get_board_status())
        return self.explore(CurrState,turn, not phase,piece)

    
    def roll_out_choose_piece(self,state:Quarto, Random_player : classmethod, turn : int )-> int : 
        player = Random_player(state)
        #winner = -1
        available_pieces = set(range(16))
        available_positions = set([ (x,y) for x in range(4) for y in range(4) ])
        while  not state.check_finished():
            piece_ok = False
            while not piece_ok:
                piece =  player.choose_piece(list(available_pieces))
                piece_ok = state.select(piece)
            available_pieces = available_pieces - set((piece,))
            piece_ok = False
            turn =  1 - turn 
            while not piece_ok:
                chosen_position = player.place_piece(list(available_positions))
                piece_ok = state.place(*chosen_position)
            available_positions = available_positions - set((chosen_position,))
            winner = state.check_winner()
            if winner != -1 : 
                 break     
            print(state.check_finished())
        return turn
    
    
    def roll_out_place_piece(self,state:Quarto, Random_player : classmethod, turn : int  )-> int : 
        player = Random_player(state)
        #winner = -1
        available_pieces = set(range(16))
        available_positions = set([ (x,y) for x in range(4) for y in range(4) ])
        while  not state.check_finished():
            piece_ok = False
            while not piece_ok:
                chosen_position = player.place_piece(list(available_positions))
                piece_ok = state.place(*chosen_position)

            available_positions = available_positions - set((chosen_position,))
            winner = state.check_winner() 
            print(state.get_board_status())
            if winner != -1 or not state.check_finished():                  
                 break     
            piece_ok = False
            while not piece_ok:
                piece = player.choose_piece(list(available_pieces))
                piece_ok = state.select(piece)

            piece 
            available_pieces = available_pieces - set((piece,))
            turn = 1 - turn 
            print(state.check_finished())

            
        return  turn    
    def expand(self,state : Quarto , phase : bool, player: bool,piece : int) -> None: 
        LOG.debug(f"Expanding state {state}")
        
        state_hash = self.hashing(state,player,phase,piece) 
        self.states_to_nodes[state_hash] = self.Node(state,phase,player,piece) 
        self.history.add(state_hash)
                
    def update(self,outcome: int )-> None:
        for history_step in self.history: 
            if outcome == 0 : 
                self.states_to_nodes[history_step].Q +=1 
            self.states_to_nodes[history_step].N +=1
        self.walked = set()
                       
    def iterate(self,state: Quarto, phase: bool, player : bool)-> None : 
        start_time = time.process_time()
        num_rollouts = 0
        
        LOG.debug(f"New iteration from state {state}")
        # LOG.debug(f" * States: {self.states_to_nodes}")
        LOG.debug(f" * Nb States: {len(self.states_to_nodes)}")
        while time.process_time() - start_time < self.time_limit: 
            if self.hashing(state,player,phase,-1) not in self.states_to_nodes: 
                self.expand(state,phase,player,-1)   

            #player , phase  = self.get_player_and_phase(player, phase)    
            explored_state,new_player ,new_phase,piece = self.explore(state,player, phase,-1)    
            
            self.expand(explored_state,new_phase,new_player,piece)
            #print(explored_state.get_board_status())
            if new_phase :       
                outcome = self.roll_out_choose_piece(explored_state, RandomPlayer,1-int(new_player))
            else : 
                outcome = self.roll_out_place_piece(explored_state , RandomPlayer,1-int(new_player))
            self.update(outcome)
            num_rollouts+= 1 
            print(num_rollouts)
        self.run_time = time.process_time() - start_time 
        self.num_rollouts = num_rollouts
    @staticmethod
    def get_player_and_phase(player , phase)-> tuple:
        return player ^ phase ,not  phase 
        
    @staticmethod 
    def hashing(state: Quarto, player : bool , phase : bool , piece : int) : 
        if  phase : 
            code =  (str(state.get_board_status()) ,str(player) ,str(phase))
        else : 
            code = (str(state.get_board_status()) ,str(player) ,str(phase),str(piece))
        
        return hash("#".join(code))
    
    def choose_best_move(self,state : Quarto, phase : bool):    
        scores = dict()
        state_hash = self.hashing(state,True,phase,-1)
        node = self.states_to_nodes[state_hash]
        for move , state_node_hash in node.children.items(): 
            if state_node_hash is None : 
                LOG.debug(f"unexplored move {move}")
                continue 
            state_node = self.states_to_nodes[state_node_hash]
            Q = state_node.Q 
            N = state_node.N 
            win_ratio = Q/N 
            scores[move] = win_ratio
        LOG.debug(f"Actions : {scores}")
        return max(scores , key = lambda k : scores[k])
        

    def choose_piece(self)-> int: 
        phase = True 
        player = True

        state = deepcopy(self.quarto_state)
        
        self.iterate(state,phase,player) 
        LOG.debug(f"states_to_nodes : {self.states_to_nodes}")
        LOG.debug(f" time : {self.run_time}, roll outs : {self.num_rollouts}")
        return   self.choose_best_move(state,True)  
        

          
    def place_piece(self)->tuple[int,int] :
        phase = False 
        player = True
        state = deepcopy(self.quarto_state)
        print(state.get_board_status())
        self.iterate(state,phase , player)
        LOG.debug(f"states_to_nodes : {self.states_to_nodes}")
        LOG.debug(f" time : {self.run_time}, roll outs : {self.num_rollouts}")
        return   self.choose_best_move(state, False)      
        
    
    #def statistics(self) -> tuple: 
    #    return self.num_rollouts , self.run_time 
        
        
        