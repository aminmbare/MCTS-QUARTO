import time 
from quarto import Quarto, Player
from copy import deepcopy
from math import sqrt, log
import numpy as np
import logging
from operator import and_ 
from functools import reduce , cache 
import matplotlib.pyplot as plt
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
        self.FLAG = None
        
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
        self.forbidden_pieces = list()
    def select_node(self,state : Quarto,phase : bool , player : bool) -> tuple:
        node = self.root
        CurrState = deepcopy(state)

        while len(node.children) != 0:
            children = node.children.values()
            max_value = max(children, key=lambda n: n.value()).value()
            max_nodes = [n for n in children if n.value() == max_value]

            node = random.choice(max_nodes)
            player = node.player
            phase = node.phase
            #print(type(node.move))
            if type(node.move) is tuple:
                CurrState.place(*node.move)
            else :                        
                CurrState.select(node.move)
            if node.N == 0:
                new_player , phase =self.get_player_and_phase(player , phase )
                return node, CurrState, phase, new_player
            player , phase =self.get_player_and_phase(player , phase )
            #new_player , new_phase =self.get_player_and_phase(player , phase )
        if self.expand(node, CurrState,phase,player):
            node = random.choice(list(node.children.values()))
            if type(node.move) is tuple:
                CurrState.place(*node.move)
            else: 
                CurrState.select(node.move)
        new_player , new_phase =self.get_player_and_phase(player , phase)
        #print(new_player)
        return node, CurrState,new_phase, new_player
    @staticmethod
    def get_player_and_phase(player , phase)-> tuple:
        return player ^ phase ,not  phase 
    
    def scores(self): 
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        best_child = random.choice(max_nodes)
        return best_child.move
    
    
    def expand(self, parent: Node, state: Quarto,phase : bool , player : bool) -> bool:
        if state.check_finished():
            return False
        if phase :
            children = [Node(move, parent,phase, player) for move in self.get_available_pieces(state)]
        else : 
            board = state.get_board_status()
            children = [Node((i,j), parent,phase, player) for i,j in zip(np.where(board == -1)[0],np.where(board == -1)[1]) ]

        parent.add_children(children)

        return True
    
    
    def back_propagate(self, node: Node, outcome: int) -> None:

        # For the current player, not the next player
        #reward = 0 if outcome == turn else 1
        if outcome  == 1 :
            winner = node.player
        else : 
            winner = not node.player 
        if outcome == -1 : 
            winner = None
        while node is not None:
            node.N += 1
            if  node.player == winner : 
                node.Q += 1
            node = node.parent
            #if outcome == -1:
            #    reward = 0
            #else:
            #    reward = 1 - reward
    
    
    
    def search(self,state: Quarto, phase : bool,player : True  ): 
        start_time = time.process_time()
        #random_player = RandomPlayer
        num_rollouts = 0
        #timing_1 = list()
        #timing_2 = list()
        #timing_3 = list()
        #i = 0 
        #j = 0
        while time.process_time() - start_time < self.time_limit:
            
            node, new_state , new_phase, new_player = self.select_node(state,phase,player)
            if new_phase :                    
                outcome = self.roll_out_choose_piece(new_state,RandomPlayer,node.move)         
           
            else :          

                outcome = self.roll_out_place_piece(new_state,RandomPlayer, node.move)
                
            self.back_propagate(node, outcome)
            num_rollouts += 1
        run_time = time.process_time() - start_time
        #print("average :",np.average(timing_1),np.average(timing_2), np.average(timing_3), i,j)
        self.run_time = run_time
        self.num_rollouts = num_rollouts
                                     
    def scores(self,state : Quarto):
        if state.check_finished():
            return -1

        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        best_child = random.choice(max_nodes)
        for node in self.root.children.values(): 
            print("NODE",node.move, node.N, node.Q, node.value())
        return best_child.move 
    
    def get_available_pieces(self,state:Quarto)->set:
        pieces = set(range(16))
        pieces_on_board = set()
        board = state.get_board_status()
        for i,j in zip(np.where(board != -1 )[0],np.where(board != -1 )[1]): 
           
            pieces_on_board.add(board[i,j])
        if len(self.forbidden_pieces) == 0  :
            return   pieces - pieces_on_board
        else :       
            for piece in self.forbidden_pieces : 
                pieces.remove(piece)
            self.forbidden_pieces= list()
            return pieces - pieces_on_board
    
    def choose_piece(self)-> int:
        self.time_limit = 15
        phase = True 
        state = deepcopy(self.root_state)
        board = state.get_board_status() 
        if len(board[board != -1]) >= 3 : 
                self.__prior_knowledge(state)  
        self.search(state,phase,True)
        move =self.scores(state)
        self.root = Node(None ,None,None ,True)
        print(f" time : {self.run_time}, roll outs : {self.num_rollouts}")

        return move
    
    def __prior_knowledge(self,state:Quarto)-> None: 
        available_pieces = self.get_available_pieces(state)
        print(state.get_board_status())
        print(available_pieces)
        for piece in available_pieces : 
            if self.check_board(state,piece) : 
                piece
                self.forbidden_pieces.append(piece)
        if len(self.forbidden_pieces) == len(available_pieces): 
            print(len(self.forbidden_pieces) , len(available_pieces))
            self.forbidden_pieces = list()
    def __finishing_move(self, state :Quarto)->tuple[bool,tuple]: 
        board = state.get_board_status()
        available_positions =  [(i,j)   for i,j in zip(np.where(board == -1)[0],np.where(board == -1)[1]) ]
        for pos in available_positions:
            temp_state = deepcopy(state)
            temp_state.place(*pos)
            if self.winning_move(temp_state,pos) : 
                print(pos)
                return (True,pos)
        return (False , None)
   
    def place_piece(self)->tuple[int,int] : 
        
        self.time_limit = 15
        phase = False
        state = deepcopy(self.root_state)
        board = state.get_board_status()
        if  len(board[board != -1]) > 3 : 
            outcome,move=self.__finishing_move(state)
            if outcome: 
                return move 
        self.search(state,phase,True)
        move =self.scores(state)

        self.root = Node(None ,None,None ,True)
        print(f" time : {self.run_time}, roll outs : {self.num_rollouts}")
       
        return move
    
    
    def roll_out_choose_piece(self,state:Quarto, Random_player : classmethod,move:tuple )-> int : 
        player = Random_player(state)
        winner = -1
       
        turn = 1
        depth = 0
        start = time.process_time()
        if state.check_winner() != -1: 
            return  turn 
        print("time his", time.process_time()-start)
        start = time.process_time()
        if self.heuristic_2(state,move) != -1: 
            return  turn 
        print("time my", time.process_time()-start)
        while winner < 0 and  not state.check_finished() and depth < 3:
            piece_ok = False
            while not piece_ok:
                piece_ok = state.select(player.choose_piece())
            piece_ok = False
            turn =  1 - turn 
            while not piece_ok:
                x, y = player.place_piece()
                piece_ok = state.place(x, y)
            depth +=1
            if  self.winning_move(state,(x,y)): 
                winner = turn 
                break    
                    
        return winner
       
    def roll_out_place_piece(self,state:Quarto, Random_player : classmethod, move : int)-> int: 
        player = Random_player(state)
        winner = -1
        turn = 0             
        depth = 0        
        #if state.check_winner(): 
        #    return turn
        if self.check_board(state,move): 
            return turn
        while winner < 0 and  not state.check_finished() and depth < 3:
           piece_ok = False       
           while not piece_ok:    
               x, y = player.place_piece()
               piece_ok = state.place(x, y) 
           depth +=1 
                
           if self.winning_move(state,(x,y))  :                  
               winner = turn 
               break     
           if  state.check_finished():
               break      
           piece_ok = False     
           while not piece_ok:
               piece_ok = state.select(player.choose_piece())
           turn = 1 - turn             
        return winner
    
    @staticmethod
    def winning_move(state :Quarto,move : tuple)-> bool : 
        board = state.get_board_status()
        row = board[move[0]]
        pieces = row != -1 
        
        if sum(pieces) ==4 : 
            if reduce(and_, row) != 0 or reduce(and_, row ^ 15) != 0:
                   return True 
        column = board[:,move[1]]
        pieces = column != -1
        
        if sum(pieces) == 4 : 
            if reduce(and_ , column) != 0 or reduce(and_ , column ^ 15) != 0 : 
                return True 
        
        if (move[0] == move[1]) or (3-move[0] ==  move[1]):
            for diag in [board.diagonal() , board[::-1].diagonal()]: 
                pieces = diag != -1
                if sum(pieces) == 4 : 
                    if reduce(and_, diag)!= 0 or reduce(and_ , diag ^15 ) != 0 : 
                        return True  
        return False         
    @staticmethod 
    def heuristic_2(state: Quarto, move : int )-> bool : 
        board = state.get_board_status()
        for row in board: 
            pieces = row != -1
            if sum(pieces)==3: 
                    row_temp = deepcopy(row)
                    row_temp[np.where(pieces == False)] = move 
                    if reduce(and_, row_temp) != 0 or reduce(and_, row_temp ^ 15) != 0:
                        return True
        for col in board.T : 

            pieces = col != -1 
            if sum(pieces) == 3: 
                col_temp = deepcopy(col)
                col_temp[np.where(pieces == False)] = move
                if reduce(and_, col_temp) != 0 or reduce(and_, col_temp ^ 15) != 0:  
                   return  True
        for diag in [board.diagonal(), board[::-1].diagonal()]: 
            diag = np.array(diag)
            pieces = diag != -1 
            if sum(pieces)==3 : 
                diag_temp = deepcopy(diag)
                diag_temp[np.where(pieces == False)] = move
                if reduce(and_,diag_temp) !=0 or reduce(and_,diag_temp^15) != 0 : 
                    return True
        return False           
    @staticmethod 
    def heuristic_1(state: Quarto)-> int: 
        score = 0
        board = state.get_board_status()
        for row in board: 
            pieces = row != -1
            if sum(pieces)==3: 
                    if reduce(and_, row[pieces]) != 0 or reduce(and_, row[pieces] ^ 15) != 0:
                        score += 1   
        for col in board.T : 
            pieces = col != -1 
            if sum(pieces) == 3: 
                if reduce(and_, col[pieces]) != 0 or reduce(and_, col[pieces] ^ 15) != 0:  
                    score +=1
        for diag in [board.diagonal(), board[::-1].diagonal()]: 
            pieces = diag != -1 
            if sum(pieces)==3 : 
                if reduce(and_,diag[pieces]) !=0 or reduce(and_,diag[pieces]^15) != 0 : 
                    score +=1
        return score           
        
    #@cache 
    def alpha_beta(self,state : Quarto ,alpha : float , beta : float , MaximizingPlayer : bool , phase : bool,depth : int):
        
        if depth >=  3 and phase :
            return self.check_board(state) if MaximizingPlayer else -self.check_board(state)
             
        if phase : 
            if state.check_winner(): 
                return 10 if MaximizingPlayer else -10
            moves =  self.get_available_pieces(state)
        else : 
            board = state.get_board_status()
            moves =[  (i,j) for i,j in zip(np.where(board == -1)[0],np.where(board == -1)[1]) ] 
        
        scores = list()  
        if MaximizingPlayer : 
            player = MaximizingPlayer ^ phase 
            for i in moves : 
                temp_state = deepcopy(state)   
                evaluation = self.alpha_beta(temp_state.select(i) if phase else temp_state.select(*i),alpha , beta ,player,not phase, depth+1  ) 
                scores.append(evaluation)
                alpha = max(alpha , evaluation)
                if beta <= alpha : 
                    break 
            return max(scores)
        else : 
            player = MaximizingPlayer ^ phase         
            for i in moves : 
                temp_state = deepcopy(state)
                evaluation = self.alpha_beta(temp_state.select(i) if phase else temp_state.select(*i),alpha , beta , player , not phase, depth+1)
                scores.append(evaluation)
                beta = min(beta , evaluation)
                if beta <=alpha : 
                    break 
            return min(scores)