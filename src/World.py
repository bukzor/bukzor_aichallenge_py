"""
The world class keeps track of all world state.
"""
from collections import defaultdict, namedtuple
from math import sqrt
from random import seed
from time import time

from Map import Map

class World(object):
    "A container for all the world state in the game"
    def __init__(self, gameparams):

        self.turns = gameparams['turns']

        self.time = namedtuple('turn', 'load', 'turn_start')(
                gameparams['turntime'],
                gameparams['loadtime'],
                time(),
        )

        self.radius = namedtuple('view', 'attack', 'spawn')(
                gameparams['viewradius2'],
                gameparams['attackradius2'],
                gameparams['spawnradius2'],
        )

        self.list = namedtuple('hill', 'ant', 'dead', 'food')(
                {}, {}, defaultdict(list), [],
        )

        seed(gameparams['player_seed'])

        self.map = Map(gameparams['rows'], gameparams['cols'])

        # These are initialized lazily
        self.__cache = namedtuple('vision_offsets', 'vision')(None, None)

    def update(self, data):
        'parse engine input and update the world state'

        # start timer
        self.time.turn_start = time()
        
        # reset vision
        self.__cache.vision = None
        
        # clear hill, ant and food data
        for row, col in (
                self.list.ant.keys() +
                self.list.dead.keys() +
                self.list.food
        ):
            self.map[row][col] = Map.LAND
        self.list.hill.clear()
        self.list.ant.clear()
        self.list.dead.clear()
        del self.list.food[:]
        
        # update map and create new ant and food lists
        for line in data.split('\n'):
            tokens = line.strip().lower().split()
            if not tokens:
                continue

            key = tokens[0]
            row = int(tokens[1])
            col = int(tokens[2])
            if len(tokens) == 3:
                if key == 'w':
                    self.map[row][col] = Map.WATER
                    continue
                elif key == 'f':
                    self.map[row][col] = Map.FOOD
                    self.list.food.append((row, col))
                    continue
            elif len(tokens) == 4:
                owner = int(tokens[3])
                if key == 'a':
                    self.map[row][col] = owner
                    self.list.ant[(row, col)] = owner
                    continue
                elif key == 'd':
                    # food could spawn on a spot where an ant just died
                    # don't overwrite the space unless it is land
                    if self.map[row][col] == Map.LAND:
                        self.map[row][col] = Map.DEAD
                    # but always add to the dead list
                    self.list.dead[(row, col)].append(owner)
                    continue
                elif key == 'h':
                    self.list.hill[(row, col)] = owner
                    continue

            raise ValueError("Could not interpret input line: %r" % line)
                        
    def time_remaining(self):
        "How much time is left?"
        return self.time.turn - int(1000 * (time() - self.time.turn_start))
    
    def my_hills(self):
        "Where are my hills?"
        return [loc for loc, owner in self.list.hill.items()
                    if owner == Map.MY_ANT]

    def enemy_hills(self):
        "Where are their hills?"
        return [(loc, owner) for loc, owner in self.list.hill.items()
                    if owner != Map.MY_ANT]
        
    def my_ants(self):
        "return a list of all my ants"
        return [(row, col) for (row, col), owner in self.list.ant.items()
                    if owner == Map.MY_ANT]

    def enemy_ants(self):
        "return a list of all visible enemy ants"
        return [((row, col), owner)
                    for (row, col), owner in self.list.ant.items()
                    if owner != Map.MY_ANT]

    def food(self):
        "return a list of all food locations"
        return self.list.food[:]

    def visible(self, loc):
        "Which squares are visible to me?"
        # todo: this should return a Map of some kind

        if self.__cache.vision is None:
            if self.__cache.vision_offsets is None:
                # precalculate squares around an ant to set as visible
                self.__cache.vision_offsets = []
                offset = int(sqrt(self.radius.view))
                for d_row in range(-offset, offset+1):
                    for d_col in range(-offset, offset+1):
                        radius2 = d_row**2 + d_col**2
                        if radius2 <= self.radius.view:
                            self.__cache.vision_offsets.append((
                                # Create all negative offsets so vision will
                                # wrap around the edges properly
                                (d_row % self.map.rows) - self.map.rows,
                                (d_col % self.map.cols) - self.map.cols
                            ))
            # set all spaces as not visible
            # loop through ants and set all squares around ant as visible
            self.__cache.vision = [
                    [False]*self.map.cols for row in range(self.map.rows)
            ]
            for ant in self.my_ants():
                a_row, a_col = ant
                for v_row, v_col in self.__cache.vision_offsets:
                    self.__cache.vision[a_row + v_row][a_col + v_col] = True
        row, col = loc
        return self.__cache.vision[row][col]


# vim: expandtab sts=4 sw=4
