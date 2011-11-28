"""
The Map tries to fully represent the game grid: ants, land, food, and water.
"""

class Map(object):
    "A representation of the game grid"
    MY_ANT = 0
    ANTS = 0
    DEAD = -1
    LAND = -2
    FOOD = -3
    WATER = -4
    
    AIM = {'n': (-1, 0),
        'e': (0, 1),
        's': (1, 0),
        'w': (0, -1)}

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.__map = [[Map.LAND] * self.cols for _ in range(self.rows)]

    def __iter__(self):
        return iter(self.__map)

    def __getitem__(self, key):
        return self.__map[key]

    def destination(self, loc, direction):
        "calculate a new location given the direction and wrap correctly"
        row, col = loc
        d_row, d_col = Map.AIM[direction]
        return ((row + d_row) % self.rows, (col + d_col) % self.cols)        

    def passable(self, loc):
        "true if not water"
        row, col = loc
        return self[row][col] != Map.WATER
    
    def unoccupied(self, loc):
        "true if no ants are at the location"
        row, col = loc
        return self[row][col] in (Map.LAND, Map.DEAD)

    def distance(self, loc1, loc2):
        "calculate the closest distance between to locations"
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row + d_col

    def direction(self, loc1, loc2):
        "determine the 1 or 2 fastest (closest) directions to reach a location"
        row1, col1 = loc1
        row2, col2 = loc2
        height2 = self.rows//2
        width2 = self.cols//2
        results = []
        if row1 < row2:
            if row2 - row1 >= height2:
                results.append('n')
            if row2 - row1 <= height2:
                results.append('s')
        if row2 < row1:
            if row1 - row2 >= height2:
                results.append('s')
            if row1 - row2 <= height2:
                results.append('n')
        if col1 < col2:
            if col2 - col1 >= width2:
                results.append('w')
            if col2 - col1 <= width2:
                results.append('e')
        if col2 < col1:
            if col1 - col2 >= width2:
                results.append('e')
            if col1 - col2 <= width2:
                results.append('w')
        return results

    def __str__(self):
        'return a pretty string representing the map'
        player_ant = 'abcdefghij'
        hill_ant = 'ABCDEFGHIJ'
        player_hill = '0123456789'
        map_object = '?%*.!'
        map_render = player_ant + hill_ant + player_hill + map_object

        tmp = ''
        for row in self:
            tmp += '# %s\n' % ''.join([map_render[col] for col in row])
        return tmp

# vim: expandtab sts=4 sw=4
