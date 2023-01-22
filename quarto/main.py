# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
import quarto
from quarto import  Myplayer, Ma

class RandomPlayer(quarto.Player):
    """Random player"""

    def __init__(self, quarto: quarto.Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)


def main():
    game = quarto.Quarto()
    mcts_1 = Myplayer.MCTS
    mcts_2 = Ma.MCTS
    Matches = 10
    game.set_players((  RandomPlayer(game), mcts_2(game)))
    wins = 0 
    draws = 0 
    loss = 0
    #winner = game.run()
    #logging.warning(f"main: Winner: player {winner}")
    for _ in range(Matches): 
        logging.warning(f"-----MATCH {_+1}-----")
        winner = game.run()
        if winner ==1 : 
            wins+= 1 
        if winner == 0 : 
            loss+=1
        if winner < 0 : 
            draws +=1
        game.reset()
        logging.warning(f"main: Winner: player {wins}, Draws {draws}, Loss {loss} ")


    logging.warning(f"main: Winner: player {wins}, Draws {draws}, Loss {loss} ")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase log verbosity')
    parser.add_argument('-d',
                        '--debug',
                        action='store_const',
                        dest='verbose',
                        const=2,
                        help='log debug messages (same as -vv)')
    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)
        
    main()
