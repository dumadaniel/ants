'''
Created on Nov 18, 2011

@author: dduma
'''
from ants import *
from AntsQueue import AntsQueue
from AntsMap import ScentMap, Square
from math import sqrt
from random import choice
import sys
import time

SCENT_FACTOR = 4.0

FOOD = 'food'
EXPLORE = 'explore'
ENEMY_HILL = 'enemy_hill'


class MyBot:
    def __init__(self, logfile=None):
        # define class level variables, will be remembered between turns
        self.log = logfile
        self.viewradius = 0
        self.scentmap = []
        self.scent_food = 0
        self.scent_water = 0
        self.scent_ant = 0
        self.scent_hill = 0
        self.enemy_hills = []
        self.my_hills = []
    
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.viewradius = int(sqrt(ants.viewradius2))
        self.scentmap = ScentMap(ants.rows, ants.cols)
        self.scent_food = SCENT_FACTOR**self.viewradius
        self.scent_explore = 4.0
        self.scent_hill = float(SCENT_FACTOR**(self.viewradius*3))
        self.my_hills = [ self.scentmap.get_square(loc) for loc in ants.my_hills() ]
    
    def do_turn(self, ants):
        
        def debug(msg):
            if self.log:
                self.log.write(msg)
        
        self.scentmap.clear()
        
        debug('TURN %s -- %s\n**********\n**********\n' % (ants.current_turn, time.asctime()))
        
        def can_smell(ant, scent):
            square = self.scentmap.get_square(ant)
            smells = False
            for adj in self.scentmap.get_adjacent_squares(square):
                if adj.get_scent(scent) != 0:
                    smells = True
            return smells
        
        def do_move(ant, target):
            loc = self.scentmap.get_square(ant)
            moves = []
            best = -sys.maxint
            for square in self.scentmap.get_adjacent_squares(loc):
                if square.scents[target] > best:
                    moves = [square]
                    best = square.scents[target]
                elif square.scents[target] == best:
                    moves.append(square)
            
            dest = choice(moves)
            direction = ants.direction(ant, dest.location())[0]
            ants.issue_order((ant, direction))
            
        for loc, owner in ants.enemy_hills():
            square = self.scentmap.get_square(loc)
            if square not in self.enemy_hills:
                self.enemy_hills.append(square)
        
        # SPREAD EXPLORE SCENT
        high = Square((10,10))
        for square in self.scentmap.get_iterator():
            if square.is_water(ants) or square.is_ant(ants) or square in self.my_hills:
                square.set_scent(EXPLORE, 0)
                continue
            if not ants.visible(square.location()):
                scent = self.scent_explore**(ants.current_turn - square.turn_last_seen)
                square.set_scent(EXPLORE, scent)
                
                if high.get_scent(EXPLORE) < scent:
                    high = square
                    
        queue = AntsQueue([high])
        visited = set()
        while len(queue) > 0:
            square = queue.dequeue()
            visited.add(square)
            
            if ants.visible(square.location()):
                scent = None
                if square.is_water(ants) or square.is_ant(ants) or square in self.my_hills:
                    scent = 0
                else:
                    scent = self.scentmap.get_adj_scent(square, EXPLORE)
            
                square.set_scent(EXPLORE, scent)
                square.seen(ants.current_turn)
            
            for adj in self.scentmap.get_adjacent_squares(square):
                if adj not in visited:
                    visited.add(adj)
                    queue.enqueue(adj)
        
        """
        for visible in self.scentmap.get_iterator():
            if ants.visible(visible.location()) and visible not in updated:
                if square.is_water(ants) or square.is_ant(ants) or square in self.my_hills:
                    visible.set_scent(EXPLORE, 0)
                    continue
                else:
                    queue = AntsQueue([visible])
                    visited = set()
                    while len(queue) > 0:
                        square = queue.dequeue()
                        visited.add(square)
                        
                        if square.is_water(ants) or square.is_ant(ants) or square in self.my_hills:
                            square.set_scent(EXPLORE, 0)
                            square.seen(ants.current_turn)
                            
                            for adj in self.scentmap.get_adjacent_squares(square):
                                if adj not in visited:
                                    visited.add(adj)
                                    queue.enqueue(adj)
                        else:
                            scent = 0
                            for adj in self.scentmap.get_adjacent_squares(square):
                                scent += adj.get_scent(EXPLORE)
                                
                                if adj not in visited:
                                    visited.add(adj)
                                    queue.enqueue(adj)
                            square.set_scent(EXPLORE, scent/4)
                            square.seen(ants.current_turn)
        """
        
        # SPREAD FOOD SCENT
        for food in ants.food():
            root_square = self.scentmap.get_square(food)
            root_square.set_scent(FOOD, self.scent_food)
            
            queue = AntsQueue([root_square])
            visited = set()
            while len(queue) > 0:
                square = queue.dequeue()
                visited.add(square)
                
                if square.is_food(ants):
                    square.set_scent(FOOD, self.scent_food)
                    
                    for adj in self.scentmap.get_adjacent_squares(square):
                        if adj not in visited:
                            visited.add(adj)
                            queue.enqueue(adj)
                elif square.is_water(ants) or square.is_ant(ants):
                    square.set_scent(FOOD, 0)
                    
                    for adj in self.scentmap.get_adjacent_squares(square):
                        if adj not in visited:
                            visited.add(adj)
                            queue.enqueue(adj)
                else:
                    scent = 0
                    for adj in self.scentmap.get_adjacent_squares(square):
                        scent += adj.get_scent(FOOD)
                        
                        if adj not in visited:
                            visited.add(adj)
                            queue.enqueue(adj)
                    scent /= 4
                    square.set_scent(FOOD, scent)
            
        for square in self.scentmap.get_iterator():
            if FOOD not in square.all_scents():
                scent = 0
                for adj in self.scentmap.get_adjacent_squares(square):
                    scent += adj.get_scent(FOOD)
                square.set_scent(FOOD, scent/4)
                
        # SPREAD ENEMY HILL SCENT 
        for hill in self.enemy_hills:
            queue = AntsQueue([hill])
            visited = set()
            
            while len(queue) > 0:
                square = queue.dequeue()
                visited.add(square)
                
                if square in self.enemy_hills:
                    square.set_scent(ENEMY_HILL, self.scent_hill)
                    
                    for adj in self.scentmap.get_adjacent_squares(square):
                        if adj not in visited:
                            visited.add(adj)
                            queue.enqueue(adj)
                elif square.is_water(ants) or square.is_ant(ants): #or square.location() in [loc for loc,owner in ants.enemy_ants()]:
                    square.set_scent(ENEMY_HILL, 0)
                    
                    for adj in self.scentmap.get_adjacent_squares(square):
                        if adj not in visited:
                            visited.add(adj)
                            queue.enqueue(adj)
                else:
                    scent = 0
                    for adj in self.scentmap.get_adjacent_squares(square):
                        scent += adj.get_scent(ENEMY_HILL)
                        
                        if adj not in visited:
                            visited.add(adj)
                            queue.enqueue(adj)
                    square.set_scent(ENEMY_HILL, scent/4)
                    
        attackers = 0
        for ant in ants.my_ants():
            if can_smell(ant, ENEMY_HILL):
                attackers += 1
        
        goals = {FOOD : 0, EXPLORE : 0, ENEMY_HILL: 0}
        for ant in ants.my_ants():
            goal = None
            if len(self.enemy_hills)>0 and can_smell(ant, ENEMY_HILL) and len(ants.my_ants())/attackers <= 10:
                goal = ENEMY_HILL
                goals[ENEMY_HILL] += 1
            elif can_smell(ant, FOOD):
                goal = FOOD
                goals[FOOD] += 1
            else:
                goal = EXPLORE
                goals[EXPLORE] += 1
            
            do_move(ant, EXPLORE)
            
        debug('FOOD moves: %s\n' % goals[FOOD])
        debug('EXPLORE moves: %s\n' % goals[EXPLORE])
        debug('ENEMY_HILL moves: %s (Known: %s)\n' % (goals[ENEMY_HILL],len(self.enemy_hills)))
        debug('**********\n')
            
        def getdebugval(val):
            f = self.scent_food
            
            if f == val:
                return 9
            elif f > val >= f/4:
                return 8
            elif f/4 > val >= f/(4**2):
                return 7
            elif f/(4**2) > val >= f/(4**3):
                return 6
            elif f/(4**3) > val >= f/(4**4):
                return 5
            elif f/(4**4) > val >= f/(4**5):
                return 4
            elif f/(4**5) > val >= f/(4**6):
                return 3
            elif f/(4**6) > val >= f/(4**7):
                return 2
            elif f/(4**7) > val >= f/(4**8):
                return 1
            else:
                return 0
            
        """
        for r in xrange(self.scentmap.rows):
            l = []
            for c in xrange(self.scentmap.cols):
                curr = self.scentmap.get_square((r,c))
                if curr.is_ant(ants):
                    l.append('A')
                elif curr.is_food(ants):
                    l.append('F')
                else:
                    l.append(str(getdebugval(curr.scents[FOOD])))
            debug('%s\n' % ' '.join(l))
        """
        
        debug('Time used: %s of %s\n' % ((ants.turntime-ants.time_remaining()), ants.turntime))

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        #log = open('','w')
        Ants.run(MyBot())
        #log.close()
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
