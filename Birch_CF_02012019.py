# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:16:42 2018

@author: wukak
"""

import numpy as np 


B = 2  # how many children can non_leaf node have
L = 3  # how many children can leaf have 
SPLITNODE = (B+1)/2  # the number of children to split when spliting Node
SPLITLEAF = (L+1)/2  # the number of children to split when spliting Leaf
T = 10000  # radius
VALUE_D = 2
nodecount = 0
MAXNUMBER = 999999



# Global function
def distance(entry_value_a,entry_value_b):  # Euclidean distance between two entries
    dis = 0.0
    for dim in range(VALUE_D):
        dis += np.square(entry_value_a[dim] - entry_value_b[dim])
    return np.sqrt(dis)

def info(instance):
    if instance.type == 'Entry':
        print instance.value
        print instance.level
        print instance.type
    else:
        print 'id: %d' % instance.id
        print instance.type
        print 'N: %d' % instance.N
        print 'level: %d' % instance.level
        print instance.LS
        print instance.SS 

# NON-LEAF NODE
class Node:
    def __init__(self):
        global nodecount
        self.id = nodecount
        nodecount += 1
        
        self.N = 0  # number of entries
        self.LS = np.zeros(VALUE_D)  # linear sum of entries
        self.SS = np.zeros(VALUE_D)  # square sum of entries
        self.is_root = True
        self.parent = None  # parent node
        self.children = []
        self.level = 0  # in which level of the tree
        self.type = 'Node'
        
    
    def split(self):
        if self.N <= B:
            print 'DIDNT EXCEED'
            return False
        
        inserted_child = self.children[-1]  # select the child just added
        distances = []  # to store the distance with the child just added         
        for child in self.children:
            distances.append(distance(inserted_child.LS/float(inserted_child.N),child.LS/float(child.N)))
        rank = np.argsort(distances)[::-1]  # sorted by the order of distance to siblings
        newParentNode = Node()
        
        # the children which is far enough to have other parents
        for i in range(SPLITNODE):
            child = self.children[rank[i]]
            # assign the child to newParent
            newParentNode.addChild(child)
        
        # refresh the children list of the original parent and related infomation
        self.children = [selchild for selchild in self.children if selchild not in newParentNode.children]
        self.N = 0  # refresh N
        self.LS = np.zeros(VALUE_D)
        self.SS = np.zeros(VALUE_D)
        for child in self.children:
            self.N += child.N
            self.LS += child.LS
            self.SS += child.SS
        
        # newParentNode's parent should be the parent of the original parent
        if self.is_root is False:
            self.parent.addChild(newParentNode)
        else:
            newGrandParent = Node()
            newGrandParent.addChild(self)
            newGrandParent.addChild(newParentNode)
        self.is_root = False        
        
        # refresh level
        self.refreshLevel()
        
        return True
    
    
    def check(self):  # check if the number of the siblings is legal
        if len(self.children) > B:  # number of direct children
            self.split()
        return True
    
    
    def insert(self,entry_i):  # insert an entry to a node
        if entry_i.type != 'Entry':
            print self.id
            print 'erro insert of node'
        if self.N == 0:
            print 'exposed Node'
            return False      
        
        # find the closest child
        best_child = None
        smallest_dis = MAXNUMBER
        for child in self.children:
            dis = distance(entry_i.value,child.LS/float(child.N))  # get the distance to a child
            if dis < smallest_dis:
                best_child = child
                smallest_dis = dis   
                
        # insert to the best child
        if best_child.type == 'Node':
            best_child.insert(entry_i)
        elif best_child.type == 'Leaf':
            dis = distance(entry_i.value,best_child.LS/float(best_child.N))  # judge if the distance <= T
            if dis <= T: # within the leaf's children 
                best_child.insert(entry_i)
            else: # get a new child leaf if the entry is not allowed in the existing child
                newChildLeaf = Leaf()
                self.addChild(newChildLeaf)
                newChildLeaf.insert(entry_i)
                self.check()
        else:
            print 'exposed Node to entry'
            return False
        
        # check if the node's children are still legal
        self.check()
        
        #refresh info
        self.N = 0
        self.LS = np.zeros(VALUE_D)
        self.SS = np.zeros(VALUE_D)
        for child in self.children:
            self.N += child.N
            self.LS += child.LS
            self.SS += child.SS
        
        return True
    
    
    def addChild(self,childNode):  # insert a child Node
        self.N += childNode.N
        self.LS += childNode.LS
        self.SS += childNode.SS
        self.children.append(childNode)
        childNode.parent = self
        childNode.is_root = False
        childNode.level = self.level+1
        return True
    
    def refreshLevel(self):
        if self.is_root != True:
            self.level = self.parent.level + 1
        for child in self.children:  # up to down refresh level
            child.refreshLevel()


class Leaf:
    def __init__(self):
        global nodecount
        self.id = nodecount
        nodecount += 1 
        
        self.N = 0  # number of entries
        self.is_root = True
        self.LS = np.zeros(VALUE_D)  # linear sum of entries
        self.SS = np.zeros(VALUE_D)  # square sum of entries
        self.parent = None  # parent node
        self.children = []  # entries belonging to this leaf
        self.level = 0  # in which level of the tree
        self.type = 'Leaf'

        
    def getCF(self):
        if self.N == 0:
            return 0
        else:
            self.LS = np.zeros(VALUE_D)
            self.SS = np.zeros(VALUE_D)
            for child in self.children:
                for dim in range(VALUE_D):
                    self.LS[dim] += child.value[dim]
                    self.SS[dim] += np.square(child.value[dim])
        return self.LS,self.SS
                   
     
    def split(self):
        if self.N <= L:
            print 'DIDNT EXCEED'
            return False
        
        inserted_child = self.children[-1]  # select the child just added
        distances = []  # to store the distance with the child just added 
        for child in self.children:
            distances.append(distance(inserted_child.value,child.value))
        rank = np.argsort(distances)[::-1]
        newParentLeaf = Leaf()
        
        # the children which is far enough to have other parents
        for i in range(SPLITLEAF):
            child = self.children[rank[i]]
            # assign the child to newParent
            newParentLeaf.insert(child)
            
        # refresh the children list of the original parent and related infomation
        self.children = [selchild for selchild in self.children if selchild not in newParentLeaf.children]
        self.N = len(self.children)
        self.getCF()
        
        # newParentleaf's parent should be the parent of the original parent
        if self.is_root is False:
            self.parent.addChild(newParentLeaf)
        else:
            newParentNode = Node()
            newParentNode.addChild(self)
            newParentNode.addChild(newParentLeaf)
        self.is_root = False
             
    
    def check(self):
        if self.N > L:  # number of direct children(also N)
            self.split()
        return True
        
    
    def insert(self,entry_i):  # insert an entry
        self.children.append(entry_i)
        entry_i.parent = self
        self.N += 1
        self.getCF()  # get LS and SS
        for child in self.children:  # get level for child entry
            child.level = self.level+1
        self.check()
        return True
    
    def refreshLevel(self):  # up to down refresh
        if self.parent != None:
            self.level = self.parent.level + 1
        for child_entry in self.children:
            child_entry.refreshLevel()
        

class Entry:
    def __init__(self,value):
        self.name = None  # the name of the entry
        self.value = value  # the value of the entry
        self.parent = None  # parent leaf
        self.level = 0  # in which level of the tree
        self.type = 'Entry'
    
    def refreshLevel(self):
        self.level = self.parent.level + 1
        
        
        
if __name__ == '__main__':
    
    l = Leaf()
    a=Entry((2,5))
    b=Entry((4,9))
    c=Entry((3,7))
    d=Entry((3,2))
    l.insert(a)
    l.insert(b)
    l.insert(c)
    l.insert(d)     
    par = l.parent
    sib = par.children[1]   
    par.insert(d)
    par.insert(a)
    gra = par.parent
    

        