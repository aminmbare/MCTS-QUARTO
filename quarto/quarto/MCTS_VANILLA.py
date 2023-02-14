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

class Node: 
    def __init__(self,move,parent, phase : bool, player : bool):
        self.move = move 
        self.parent = parent 
        self.N = 0 
        self.Q = 0 
        self.children = dict()
        self.phase = phase
        self.player = player 
        self.FLAG = False 
        
    def add_children(self, children :list)-> None: 
        for child in children : 
            self.children[child.move] = child
            
    def value(self) -> float : 
        if self.N == 0 :
            return 1000000
        else : 
            return self.Q /self.N + C * sqrt(log(self.parent.N/self.N))
        
        
        
class MCTS_VANILLA(Player):
    def __init__(self,quarto):
        self.root_state  = quarto
        self.root = Node(None ,None,None ,True )

        self.node_count = 0 
        self.num_rollouts = 0 
        self.forbidden_pieces = list()
    
    ## SEARCHING THROUGH THE TREE AND SELECT NODE FOR ROLL-OUT PHASE OR EXPANSION
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
            if type(node.move) is tuple:
                CurrState.place(*node.move)
            else :                        
                CurrState.select(node.move)
            if node.N == 0:      
                return node, CurrState, not phase
            player , phase =self.get_player_and_phase(player , phase )

        if self.expand(node, CurrState,phase,player):
            node = random.choice(list(node.children.values()))
            if type(node.move) is tuple:
                CurrState.place(*node.move)
            else:   
                CurrState.select(node.move)
            return node, CurrState, not phase
        else : 
            return node , CurrState , phase 
    
    @staticmethod
    def get_player_and_phase(player , phase)-> tuple:
        return player ^ phase ,not  phase 
    '''METHODS THAT FINDS THE ALL AVAILABLE POSITIONS ON THE BOARD'''
    def get_available_positions(state: Quarto)->list: 
        moves = list()
        for i, row in enumerate(state.get_board_status()): 
            for j,element in enumerate(row): 
                if element == -1 : 
                    moves.append((i,j))     
        return moves            
    def scores(self): 
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        best_child = random.choice(max_nodes)
        return best_child.move
    
    ## EXPANSION PHASE 
    def expand(self, parent: Node, state: Quarto,phase : bool , player : bool) -> bool:
        
        if state.check_winner() !=-1 or state.check_finished() :
            return False
        if (not phase) and (parent.move is not None) : 

            if  self.heuristic_2(state,parent.move) : 
                parent.FLAG = True 
                return False 
                
        if phase :
            children = [Node(move, parent,phase, player) for move in self.get_available_pieces(state)]
        else : 
            board = state.get_board_status()
            children = [Node((i,j), parent,phase, player) for i,j in zip(np.where(board == -1)[0],np.where(board == -1)[1]) ]

        parent.add_children(children)

        return True
    
    ## BACK PROPAGATION PHASE 
    def back_propagate(self, node: Node, outcome: int) -> None:
        
        if outcome == 1 :
            winner = node.player
        elif outcome == 0 : 
            winner = not node.player 
        else: 
            winner = None
        while node is not None:
            node.N += 1
            if  node.player == winner : 
                node.Q += 1
            node = node.parent
    
    
    '''SEARCH METHOD ( NODE SELECTION +EXPANSION + ROLLOUT + BACKPORPAGATION )'''
    def search(self,state: Quarto, phase : bool,player : True  ): 
        start_time = time.process_time()
        num_rollouts = 0
        while time.process_time() - start_time < self.time_limit:

            node, new_state , new_phase = self.select_node(state,phase,player)
            if new_phase :                   
                outcome = self.roll_out_choose_piece(new_state,RandomPlayer,node.move)         
               
            else :                  
                if not node.FLAG : 
                    outcome = self.roll_out_place_piece(new_state,RandomPlayer)
                else : 
                    outcome =  0       
            
            self.back_propagate(node, outcome)
            num_rollouts += 1
        run_time = time.process_time() - start_time
        self.run_time = run_time
        self.num_rollouts = num_rollouts
                                     
    def scores(self,state : Quarto):
        if state.check_finished():
            return -1
                    
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        best_child = random.choice(max_nodes)
        return best_child.move 
    '''GET AVAILABLE PIECES TO SELECT'''
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
    
    '''KNOWLEDGE BASED APPROACH'''
    ''' FIND THE PIECES THAT COULD LEAD TO A FINISHING MOVE THUS LOSING THE GAME , HOWEVER THIS APPLIES TO THE NODES CONNECTED TO THE ROOT NODE'''
    '''  IF ALL AVAILABLE PIECES COULD LEAD TO A ¨POTENTIAL LOSS , JUST CANCEL  THIS PROCESS AND WISH THAT THE OPPONENT MAKES A MISTAKE '''
    def __prior_knowledge(self,state:Quarto)-> None: 
        available_pieces = self.get_available_pieces(state)

        for piece in available_pieces : 
            if self.heuristic_2(state,piece) : 
                self.forbidden_pieces.append(piece)
        if len(self.forbidden_pieces) == len(available_pieces): 
            self.forbidden_pieces = list()
    '''AVOID DOING MCTS IF WE HAVE THE OPPORTUNITY TO PERFORM A GAME FINISHED MOVE'''
    def __finishing_move(self, state :Quarto)->tuple[bool,tuple]: 
        board = state.get_board_status()
        available_positions =  [(i,j)   for i,j in zip(np.where(board == -1)[0],np.where(board == -1)[1]) ]
        for pos in available_positions:
            temp_state = deepcopy(state)
            temp_state.place(*pos)
            if self.heuristic_1(temp_state,pos): 

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
    
    '''ROLL OUT FOR PIECE SELECTION PHASE'''
    def roll_out_choose_piece(self,state:Quarto, Random_player : classmethod,move:tuple )-> int : 
        player = Random_player(state)
        winner = -1
       
        turn = 1
        depth = 0
        if self.heuristic_1(state,move): 
            return  turn 
        while winner < 0 and  not state.check_finished() and depth < 6:

            piece_ok = False
            while not piece_ok:
                piece_ok = state.select(player.choose_piece())
            piece_ok = False
            turn =  1 - turn 
            while not piece_ok:
                x, y = player.place_piece()
                piece_ok = state.place(x, y)
            depth +=1
            if  self.heuristic_1(state,(x,y)): 
                winner = turn 
                break    
                    
        return winner
    '''ROLL OUT FOR PIECE PLACING PHASE'''   
    def roll_out_place_piece(self,state:Quarto, Random_player : classmethod)-> int: 
        player = Random_player(state)
        winner = -1
        turn = 0             
        depth = 0              
        while winner < 0 and  not state.check_finished() and depth < 6:

           piece_ok = False       
           while not piece_ok:    
               x, y = player.place_piece()
               piece_ok = state.place(x, y) 
           depth +=1 
                
           if self.heuristic_1(state,(x,y))  :                  
               winner = turn 
               break     
           if  state.check_finished():
               break      
           piece_ok = False     
           while not piece_ok:
               piece_ok = state.select(player.choose_piece())
           turn = 1 - turn             
        return winner
    '''METHOD FINDS WHETHER THE GAME IS FINISHED AFTER A PLAYER HAS PLACED A PIECE ON THE BOARD'''
    @staticmethod
    def heuristic_1(state :Quarto,move : tuple)-> bool : 
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
    '''THIS METHOD TAKES TAKES THE BOARD STATUS AND A PIECE, TO FIND WHETHER THE PIECE SELECTED COULD LEAD TO FINISHING MOVE'''
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
