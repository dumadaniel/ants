'''
Created on Nov 18, 2011

@author: dduma
'''
class AntsQueue:
    def __init__(self, q=[]):
        self.queue = q
    
    def enqueue(self, obj):
        self.queue.append(obj)
    
    def dequeue(self):
        obj = self.queue[0]
        
        if len(self.queue) == 1:
            self.queue = []
        else:
            self.queue = self.queue[1:]
        
        return obj
    
    def __len__(self):
        return len(self.queue)
    
    def isempty(self):
        if len(self.queue) == 0:
            return True
        else:
            return False