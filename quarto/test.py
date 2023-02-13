from operator import and_
from functools import reduce 
import numpy as np 
from copy import deepcopy 
a = np.ones((4,4) ,dtype = int)*-1
a[0,3] = 11
a[1,2] = 15
a[3,0] = 13 

def check_board(board: np.ndarray, move : int )-> bool : 
        
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
    
print(a)    
for i in range(16): 
    print(check_board(a,i))
        

