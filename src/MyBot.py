#!/usr/bin/env python
"""
The Bot represents the interface between our ants and the game server.
"""
from traceback import print_exc
from World import World

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us

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

        map_data = ''
        while(True):
            try:
                current_line = stdin.readline().rstrip()
                if current_line.lower() == 'ready':
                    world = World(map_data)
                    self.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    world.update(map_data)
                    # call the do_turn method of the class passed in
                    self.do_turn(world)
                    self.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except KeyboardInterrupt:
                raise
            except:
                # attempt to keep bot alive: don't raise an error or return
                print_exc(file=self.stderr)
                self.stderr.flush()
    
    def issue_order(self, order):
        'issue an order by writing the proper ant location and direction'
        (row, col), direction = order
        self.stdout.write('o %s %s %s\n' % (row, col, direction))
        self.stdout.flush()
        
    def finish_turn(self):
        'finish the turn by writing the go line'
        self.stdout.write('go\n')
        self.stdout.flush()
    
    
    def do_turn(self, world):
        """
        do turn is run once per turn
        """
        # loop through all my ants and try to give them orders
        # the ant_loc is an ant location tuple in (row, col) form
        for ant_loc in world.my_ants():
            # try all directions in given order
            directions = ('n', 'e', 's', 'w')
            for direction in directions:
                # the destination method will wrap around the map properly
                # and give us a new (row, col) tuple
                new_loc = world.destination(ant_loc, direction)
                # passable returns true if the location is land
                if (world.passable(new_loc)):
                    # an order is the location of a current ant and a direction
                    self.issue_order((ant_loc, direction))
                    # stop now, don't give 1 ant multiple orders
                    break
            # check if we still have time left to calculate more orders
            if world.time_remaining() < 10:
                break
            
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
