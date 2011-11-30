#!/usr/bin/env python
"""
The Bot represents the interface between our ants and the game server.

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
"""
from collections import defaultdict
from traceback import print_exc
from World import World

def token_loop(func):
    """
    Wrap a function into a token-processing loop.
    The loop will end if the function returns a value,
        but not if the function throws an exception.

    The input to the token loop is a string iterator,
        but the wrapped function recieves token lists.
    """
    def wrapped(self, input_file):
        "the wrapper"
        self.state = defaultdict(list)
        while True:
            try:
                tokens = input_file.readline().strip().lower().split()
                if not tokens:
                    continue
                val = func(self, tokens)
                if val is not None:
                    return val
            except (EOFError, StopIteration):
                break
            except KeyboardInterrupt:
                raise
            except:
                # attempt to keep bot alive: don't raise an error or return
                print_exc(file=self.stderr)
                self.stderr.flush()
                # reset the state though
                self.state = defaultdict(list)
    return wrapped

class MyBot(object):
    """
    The Bot is charged with recieving commands from the server,
    updating the internal world state, and sending commands
    back to the game server.
    """
    def __init__(self, stdin, stdout, stderr):
        """
        This method enters the input/output loop and never returns.
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.state = None

        game_params = self.get_game_params(stdin)
        self.world = World(game_params)
        self.finish_turn()
        self.take_turns(stdin)


    @token_loop
    def take_turns(self, tokens):
        " Take turns, when we're told to go. "
        if tokens[0] == 'go':
            self.world.update(self.state['map_data'])
            self.do_turn()
            self.state['map_data'] = []
        else:
            self.state['map_data'].append(tokens)

    @token_loop
    def get_game_params(self, tokens):
        """
        Get the game's initial parameters
        Currently all values are 32bit signed integers,
              except player_seed is a 64bit signed integer.
        """
        if tokens[0] == 'ready':
            return self.state
        else:
            key, val = tokens
            self.state[key] = int(val)
    
    def issue_order(self, order):
        'issue an order by writing the proper ant location and direction'
        (row, col), direction = order
        self.stdout.write('o %s %s %s\n' % (row, col, direction))
        self.stdout.flush()
        
    def finish_turn(self):
        'finish the turn by writing the go line'
        self.stdout.write('go\n')
        self.stdout.flush()
    
    
    def do_turn(self):
        """
        do turn is run once per turn
        """
        # loop through all my ants and try to give them orders
        # the ant_loc is an ant location tuple in (row, col) form
        for ant_loc in self.world.my_ants():
            # try all directions in given order
            directions = ('n', 'e', 's', 'w')
            for direction in directions:
                # the destination method will wrap around the map properly
                # and give us a new (row, col) tuple
                new_loc = self.world.map.destination(ant_loc, direction)
                # passable returns true if the location is land
                if (self.world.map.passable(new_loc)):
                    # an order is the location of a current ant and a direction
                    self.issue_order((ant_loc, direction))
                    # stop now, don't give 1 ant multiple orders
                    break
            # check if we still have time left to calculate more orders
            if self.world.time_remaining() < 10:
                break
        self.finish_turn()


            
if __name__ == '__main__':
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        import sys
        MyBot(sys.stdin, sys.stdout, sys.stderr)
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')

# vim: expandtab sts=4 sw=4
