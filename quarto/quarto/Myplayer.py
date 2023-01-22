import time 
from quarto import Quarto, Player
from copy import deepcopy
from math import sqrt, log
import numpy as np
import logging
import random
from functools import cache , lru_cache
from quarto.gx_utils import PriorityQueue
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
    def compute_ucb(w:int,n: int , N: int)-> float : 
          return w/n +C *sqrt(log(N)/n)

        
    def explore(self, state: Quarto,player: bool , phase : bool,piece : int): 
        
        CurrState = deepcopy(state)
        logging.debug(f"exploring from state {state}")      
        if CurrState.check_finished(): 
            logging.debug("game is over")
            return state, player , phase , piece
        #state = deepcopy(state)   
        ucb = dict()

        state_hash = self.hashing(CurrState,player, phase,piece)
        self.history.add(state_hash)

        node = self.states_to_nodes[state_hash]
        for move , game_hash in node.children.items(): 
            if game_hash is None : 
                logging.debug(f"Unexplored node found for action {move}")
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

            ucb[move] = self.compute_ucb(w,n,N)
            
        chosen_move = max(ucb,key = lambda k : ucb[k])
        if type(move) is tuple : 
            CurrState.place(*chosen_move)
        else : 
            CurrState.select(chosen_move)
            piece = chosen_move
        #node.children[chosen_move] = self.hashing(CurrState)
        #print(phase , piece,player , state.get_board_status())
        return self.explore(CurrState,turn, not phase,piece)

    
            
            
            
    def roll_out_choose_piece(self,state:Quarto, Random_player : classmethod)-> int : 
        logging.debug(f"roll_out choose piece")
        player = Random_player(state)
        winner = -1
        turn = 0
        #available_pieces = get_available_pieces(state)
        #available_positions = get_available_positions(state)
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
        logging.debug(f"roll_out place piece")
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
            if state.check_finished():    
                break
            piece_ok = False
            while not piece_ok:
                piece_ok = state.select(player.choose_piece())
            turn = 1 - turn 

        return winner

          
          
    def expand(self,state : Quarto , phase : bool, player: bool,piece : int) -> None: 
        logging.debug(f"Expanding state {state}")
        
        state_hash = self.hashing(state,player,phase,piece) 
        self.states_to_nodes[state_hash] = self.Node(state,phase,player,piece) 
        self.history.add(state_hash)
                
    def update(self,outcome: int , turn : bool)-> None:
        for history_step in self.history: 
            if outcome == 0 and self.states_to_nodes[history_step].player_turn == turn : 
                self.states_to_nodes[history_step].Q +=1 
            self.states_to_nodes[history_step].N +=1
        self.history = set()
                       
    def iterate(self,state: Quarto, phase: bool, player : bool)-> None : 
        start_time = time.process_time()
        num_rollouts = 0
        
        logging.debug(f"New iteration from state {state}")
        # logging.debug(f" * States: {self.states_to_nodes}")
        logging.debug(f" * Nb States: {len(self.states_to_nodes)}")
        while time.process_time() - start_time < self.time_limit: 
            if self.hashing(state,player,phase,-1) not in self.states_to_nodes: 
                self.expand(state,phase,player,-1)   

            #player , phase  = self.get_player_and_phase(player, phase)    
            explored_state,new_player ,new_phase,piece = self.explore(state,player, phase,-1)    
            
            self.expand(explored_state,new_phase,new_player,piece)
            #print(new_phase, new_player,explored_state.get_board_status())
            if new_phase :       
                outcome = self.roll_out_choose_piece(explored_state, RandomPlayer)
            else : 
                outcome = self.roll_out_place_piece(explored_state , RandomPlayer)
            #print(outcome)
            self.update(outcome,new_player)
            num_rollouts+= 1 

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
                logging.debug(f"unexplored move {move}")
                continue 
            state_node = self.states_to_nodes[state_node_hash]
            #Q = state_node.Q 
            N = state_node.N 
            #win_ratio = Q/N 
            scores[move] = N
        logging.debug(f"Actions : {scores}")
        #buffer = dict()
        #i = 0
        #print(len(self.states_to_nodes))
        #for x , y in self.states_to_nodes.items(): 
        #    if i >15 : 
        #        buffer[x] = y
        #    i+=1
        #self.states_to_nodes = buffer
        
        print(len(self.states_to_nodes))
        self.states_to_nodes = dict()
        return max(scores , key = lambda k : scores[k])
         
 
    def choose_piece(self)-> int: 
        phase = True 
        player = True

        state = deepcopy(self.quarto_state)
        
        self.iterate(state,phase,player) 
        logging.debug(f"states_to_nodes : {self.states_to_nodes}")
        print(f" time : {self.run_time}, roll outs : {self.num_rollouts}")
        return   self.choose_best_move(state,True)  
        

          
    def place_piece(self)->tuple[int,int] :
        phase = False 
        player = True
        state = deepcopy(self.quarto_state)

        self.iterate(state,phase , player)
        logging.debug(f"states_to_nodes : {self.states_to_nodes}")
        print(f" time : {self.run_time}, roll outs : {self.num_rollouts}")
        return   self.choose_best_move(state, False)      
        
    
    #def statistics(self) -> tuple: 
    #    return self.num_rollouts , self.run_time 
        
        
        