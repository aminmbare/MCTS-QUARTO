# QUARTO
Project aiming at realizing a competitive player for the board game Quarto. Made for Computational Intelligence's course (A.Y. 2022/2023).

# Monte Carlo Tree Search

There are four phases of implementing MCTS (selection, expansion, roll-out, back-propagation). 
Essentially, the algorithm is these four stages repeated under a user defined `time_limit`. Since this algorithm does not allocate a lot of resources towards un-optimal actions, it will be able to fully explore good actions under a low time constraint. Below is an illustration demonstrating one of these cycles of MCTS.


## EXPLORATION VS EXPLOITATION 
To account for the balance of exploration vs exploitation, we will use the Upper Confidence bound (also used by AlphaGo) applied to Trees to determine the value of the node. 

## DOMAIN KNOWLEDGE 

MCTS search can take many iterations to converge to a good solution, which can bean issue for more general applications that are difficult to optimise. For example, the best Go implementations can require millions of play-outs in conjunction with domain specific optimisations and enhancements to make expert moves. Luckily, the performance of the algorithm can be significantly improved using a number of techniques. 

Domain knowledge specific to the current game can be exploited in the tree to filter out implausible moves or in the simulations to produce heavy playouts that are more similar to playouts that would occur between human opponents. This means that playout results will be more realistic than random simulations and that nodes will require fewer iterationsto yield realistic reward values.

• First approach could be to bound the tree expansion. For our case we will avoid expanding node that belong to the selection phase if the respective piece to be selected could lead the opponent to make a game finishing move in the placing phase.

•  A second approach could be, during the expansion (for the selection phase) of first layer's node (the node that we will base our move on) we will limit the number of moves that could be taken during expansion , all pieces that could lead to game finishing moves during the next placing phase , wouldn't be considered. However if all available pieces could lead to game ending , we just consider them all during the expansion and wish that the opponent makes a mistake during the placing phase. 

• if there is a chance to make an immediate move that will guarantee a move . We perform straight the respective move without even performing a Monte Carlo Tree search. This is done through .

## ROLL-OUT 

### RANDOM ROLL-OUT

we are simply simulating through a random game starting from the given state in the input.But instead of simulated the whole game until someone wins or a draw. We stop after a predefined amount of moves, this is defined by the variable \texttt{depth} . 

### MIN-MAX ROLL-OUT

While uniformly random move choices in the roll-out are sufficient to guarantee the convergence of MCTS to the optimal policy, more informed roll-out strategies could improve performance .For this reason, it seems natural to use fixed-depth min-max searches for choosing rollout moves.

## RESULTS 


| First Player             | Second Player             |   Results (100 matches)  |
| ------------------------ |:-------------------------:| ------------------------:|
|  Random Player           |  MCTS (Random roll-out)   |           0-100          |  
|  MCTS (Random roll-out)  |   Random Player           |           100-0          |  
|  MCTS (MinMax roll-out)  |  MCTS (Random roll-out)   |           11-89          |
|  MCTS (Random roll-out)  |  MCTS (MinMax roll-out)   |           91-9           |  
 
## ACKNOWLEDGEMENT

https://www.harrycodes.com/blog/monte-carlo-tree-search

MCTS-Minimax Hybrids Hendrik Baier and Mark H. M. Winands, Member, IEEE





