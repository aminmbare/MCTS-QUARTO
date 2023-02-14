# QUARTO
Project aiming at realizing a competitive player for the board game Quarto. Made for Computational Intelligence's course (A.Y. 2022/2023).

# Monte Carlo Tree Search

There are four phases of implementing MCTS (selection, expansion, roll-out, back-propagation). 
Essentially, the algorithm is these four stages repeated under a user defined `time_limit`. Since this algorithm does not allocate a lot of resources towards un-optimal actions, it will be able to fully explore good actions under a low time constraint. Below is an illustration demonstrating one of these cycles of MCTS.


## EXPLORATION VS EXPLOITATION 
To account for the balance of exploration vs exploitation, we will use the Upper Confidence bound (also used by AlphaGo) applied to Trees to determine the value of the node. 

### DOMAIN KNOWLEDGE 

MCTS search can take many iterations to converge to a good solution, which can bean issue for more general applications that are difficult to optimise. For example, the best Go implementations can require millions of play-outs in conjunction with domain specific optimisations and enhancements to make expert moves. Luckily, the performance of the algorithm can be significantly improved using a number of techniques. 

Domain knowledge specific to the current game can be exploited in the tree to filter out implausible moves or in the simulations to produce heavy playouts that are more similar to playouts that would occur between human opponents. This means that playout results will be more realistic than random simulations and that nodes will require fewer iterationsto yield realistic reward values.//

