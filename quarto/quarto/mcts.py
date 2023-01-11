from objects import Quarto, Player
from copy import deepcopy
from math import sqrt, log
import numpy as np
import logging
from main import RandomPlayer

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
    for i, row in enumerate(state.get_board_status): 
        for j,element in enumerate(row): 
            if element == -1 : 
                moves.append((i,j))     
    return moves            

class Node : 
    
    def __init__(self,state : Quarto, phase : bool , player_turn : bool  ) -> None:
        self.state = state
        self.N = 0
        self.Q = 0 
        self.player_turn = player_turn
        if phase : 
            self.children={o :None for o in get_available_pieces(state) }
        else :
            self.children={o :None for o in get_available_positions(state) }    
        
    def __str__(self)-> str : 
        return  f"Node(state={self.state}, N={self.N}, Q={self.Q}, children={self.children})"
    
    
                                                
class MCTS(Player):
    def __init__(self,quarto, turn ): 
        super().__self__(quarto)
        self.states_to_moves = dict()
        self.history = set()
        self.Node = Node(quarto)
        self.turn = turn
        self.player = True ## True : player 1 , False : player 2
        self.phase = True  ##  True : selection , False : placing

    @staticmethod
    def compute_ucb(w:int,n: int , N: int,player : bool)-> float : 
        if player :
          return w/n +C *sqrt(log(N)/n)
        else : 
            return 1-w/n

    def explore(self, state: Quarto): 
        LOG.debug(f"exploring from state {state}")
        
        if state.check_finished() : 
            LOG.debug("game is over")
        CurrState = deepcopy(state)   
        ucb = dict()
        state_hash = hash(CurrState)
        self.walked.add(state_hash)
        node = self.states[state_hash]
        for move , game_hash in node.children.items(): 
            if game_hash is None :
                LOG.debug(f"Unexplored node found for action {move}")
                if type(move) is tuple : 
                    CurrState.place(*move)
                else : 
                    CurrState.select(move)
                new_hash = hash(state)
                node.children[move] = new_hash
                return state
            game_node = self.states[game_hash]
            w = game_node.Q
            n = game_node.N
            N = node.N
            player = game_node.player
            ucb[move] = compute_ucb(w,n,N,player)
        chosen_move = max(ucb,key = lambda k : ucb[k])
        if type(move) is tuple : 
            CurrState.place(*move)
        else : 
            CurrState.select(move)
        node.children[chosen_move] = hash(CurrState)
        return self.explore(CurrState)

    
    def roll_out_place_piece(self,state:Quarto, Random_player : classmethod )-> int : 
        state.set_players(Random_player(),Random_player())
        winner = -1
        state.__current_player = self.turn 
        while  not state.check_finished():
            piece_ok = False
            while not piece_ok:
                piece_ok = state.select(state.__players[state.__current_player].choose_piece())
            piece_ok = False
            state.__current_player = (state.__current_player + 1) % state.MAX_PLAYERS
            while not piece_ok:
                x, y = state.__players[state.__current_player].place_piece()
                piece_ok = state.place(x, y)
            winner = state.check_winner()
            if winner != -1 : 
                 break     
        return winner  
    
    
    def roll_out_choose_piece(self,state:Quarto, Random_player : classmethod )-> int : 
        state.set_players(Random_player(),Random_player())

        state.__current_player =1 -  self.turn 
        while  not state.check_finished():
            while not piece_ok:
                x, y = state.__players[state.__current_player].place_piece()
                piece_ok = state.place(x, y)
            winner = state.check_winner() 
            if winner != -1 :                  
                 break     
            piece_ok = False
            state.__current_player = (state.__current_player + 1) % state.MAX_PLAYERS
            while not piece_ok:
                piece_ok = state.select(state.__players[state.__current_player].choose_piece())
        return winner     
    def expand(self,state : Quarto , phase : bool, player_turn : bool) -> None: 
        LOG.debug(f"Expanding state {state}")
        
        state_hash = hash(state) 
        self.states[state_hash] = self.Node(state,phase,player_turn) 
        self.history.add(state_hash)
                
    def update(self,outcome: int )-> None:
        for history_step in self.history : 
            if outcome == 1 : 
                self.states[history_step].Q +=1 
            self.states[history_step] +=1
        self.walked = set()
                       
    def iterate(self,state: Quarto, phase: bool)-> None : 

        LOG.debug(f"New iteration from state {state}")
        # LOG.debug(f" * States: {self.states}")
        LOG.debug(f" * Nb States: {len(self.states)}")
        if hash(state) not in self.states: 
            self.expand(state,phase) 
        explored_state = self.explore(state)
        self.expand(explored_state)
        if phase : 
            outcome = self.roll_out_choose_piece(explored_state, RandomPlayer)
        else : 
            outcome = self.roll_out_place_piece(explored_state , RandomPlayer)
        self.update(outcome)
        
            

    def choose_piece(self,state : Quarto)-> int: 
            phase = True 
            player = False
            self.iterate(state,phase,player)   
            


    
          
    def place_piece(self)->tuple[int,int] :
        pass
        
        
        