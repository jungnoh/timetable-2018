import random

class student(object):
    def __init__(self,len,name=None):
        self.name = name or 'Student {0}'.format(random.randrange(100000,999999))
        self.keys = [ False for i in range(len) ]
        self.keysOriginal = []
    
    def __str__(self):
        return '{0}: {1}'.format(self.name,self.keys)
