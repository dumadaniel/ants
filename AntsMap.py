'''
Created on Nov 18, 2011

@author: dduma
'''

class Square:
    def __init__(self, loc):
        r, c = loc
        self.row = r
        self.col = c
        self.scents = {}
        self.turn_last_seen = 0
        
    def location(self):
        return (self.row, self.col)
    
    def is_visible(self, ants):
        if ants.visible(self.row, self.col):
            return True
        
    def is_water(self, ants):
        if not ants.passable((self.row, self.col)):
            return True
        
    def is_food(self, ants):
        if (self.row, self.col) in ants.food():
            return True
    
    def is_ant(self, ants):
        if (self.row, self.col) in ants.ant_list.keys():
            return True
        
    def set_scent(self, scent, val):
        self.scents[scent] = val
        
    def get_scent(self, scent):
        if scent in self.scents.keys():
            return self.scents[scent]
        else:
            return 0
        
    def all_scents(self):
        return self.scents.keys()
        
    def seen(self, turn):
        self.turn_last_seen = turn
        
class ScentMap:
    def __init__(self, rows, cols):
        self.map = [ [Square((r, c)) for c in xrange(cols)] for r in xrange(rows) ]
        self.rows = rows
        self.cols = cols
        
    def get_square(self, loc):
        row, col = loc
        return self.map[row][col]
    
    def get_adjacent_squares(self, square):
        row, col = square.location()
        squares = [self.map[self.rows-1 if row-1 < 0 else row-1][col],
                   self.map[0 if row+1 >= self.rows else row+1][col],
                   self.map[row][0 if col+1 >= self.cols else col+1],
                   self.map[row][self.cols-1 if col-1 < 0 else col-1]]
        return squares
    
    def get_adj_scent(self, square, scent):
        total = 0
        for adj in self.get_adjacent_squares(square):
            total += adj.get_scent(scent)
        return total/4
    
    def get_iterator(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                yield self.map[r][c]
                
    def clear(self):
        for square in self.get_iterator():
            square.scents = {}