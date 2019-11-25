# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 18:15:40 2019

@author: wukak
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:16:42 2018

@author: wukak
"""

import numpy as np 
import csv
import time
from sklearn.cluster import KMeans

B = 10  # how many children can non_leaf node have
L = 38  # how many children can leaf have 
SPLITNODE = (B+1)/2  # the number of children to split when spliting Node
SPLITLEAF = (L+1)/2  # the number of children to split when spliting Leaf
T = 4  # radius
VALUE_D = 12
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

        
def showTree(node):
    try:
        if node.children:
            for child in node.children:
                showTree(child)
                print child.id
    except:
        return False
    if node.is_root == True:
        print node.id
   
    
def normalise(array):
    size = len(array)
    Sum = float(np.sum(array))
    Mean = Sum/size
    Std = np.std(array)
    for i in range(size):
        array[i] = (array[i]-Mean)/Std
    return array


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
        if len(self.children) <= B:
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
    
    
    def showChildren(self):  # show division of children
        childrenDivision = []
        for child in self.children:  
            childDivisionCol = child.showChildren()  # get the list of children's divisions
            for childD in childDivisionCol:
                childrenDivision.append(childD)  # collect the divisions from the list
        return childrenDivision
    
    
    def showChildrenData(self):  # show data of children
        childrenData = []
        for child in self.children:
            childDataCol = child.showChildrenData()  # get the list of children's data
            for childD in childDataCol:
                childrenData.append(childD)  # collect the data from the list
        return childrenData
    
    
    def check(self):  # check if the number of the siblings is legal
        if len(self.children) > B:  # number of direct children
            self.split()
        return True
    
    
    def getCF(self):
        if len(self.children) !=0:  # refresh CF
            self.N = 0
            self.LS = np.zeros(VALUE_D)
            self.SS = np.zeros(VALUE_D)
            for child in self.children:
                self.N += child.N
                self.LS += child.LS
                self.SS += child.SS
        if self.parent is not None:  # refresh CF of parent
            self.parent.getCF()
    
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
        self.getCF()
        
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
    
    def getHeight(self):  # get the height of a Node
        height = 0
        if len(self.children) != 0:
            height = self.children[0].getHeight() + 1
        return height

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
            print self.id
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
      
    def showChildren(self):  # show division of matches
        childrenDivision = []
        for child in self.children:
            childrenDivision.append(child.division)
        return childrenDivision
    
    def showChildrenData(self):  # show data of matches
        childrenData = []
        for child in self.children:
            childrenData.append(child.value)
        return childrenData

    def getHeight(self):  # get the height of a Leaf
        height = 0
        if len(self.children) != 0:
            height = self.children[0].getHeight() + 1
        return height


class Entry:
    def __init__(self,value,index,division):
        self.name = None  # the name of the entry
        self.value = value  # the value of the entry
        self.parent = None  # parent leaf
        self.level = 0  # in which level of the tree
        self.type = 'Entry'
        self.children = []  # fixed []
        self.index = index  # index in data
        self.division = division  # division of the match
    
    def refreshLevel(self):
        self.level = self.parent.level + 1
        
    def getHeight(self):
        return 0
       
        
    
if __name__ == '__main__':
    

# COLLECTION AND CLEANING OF DATA
    
    with open('FootballEurope_sel.csv','r') as csvFile:
        reader = csv.reader(csvFile)
        data = []
        for line in reader:
            if 'NA' not in line:
                data.append(line)
    data = np.array(data)[1:]
    division = data[:,-1]  # division
    data = data[:,:-1].astype('float64')  # data
    
    number_attr = np.shape(data)[1]  # attribute number
    for attr in range(number_attr/2):
        data[:,attr*2] += data[:,attr*2+1]
        data[:,attr*2] = normalise(data[:,attr*2])
        
    merged_data = data[:,[i for i in range(number_attr) if i%2 == 0]]  # merge the data of home and away
    
    # Shot total,  Shot on target,  interception,  Tackles total,   Tackles success,  Foul commited,
    # Passes key,  Passes sucess,   Possession,    Dribble succes,  Aerials total,    Corners     
    

# CLUSTERING
    
#    # Birch
#    
#    massdata = np.array(list(merged_data)*100)  # testing dataset
#    massdivision = np.array(list(division)*100)
#    root = Leaf()
#    size = len(massdata)    
#    starttime = time.time()
#    for match_no in range(size):
#        while root.is_root != True:  # get the real root
#            root = root.parent
#        root.insert(Entry(massdata[match_no],match_no,massdivision[match_no]))
#          
#    endtime = time.time()
#    time_used = endtime - starttime
#    print('USING TIME %f' % time_used)
    
    # Kmeans
    starttime = time.time()
    massdata = np.array(list(merged_data)*10)  # testing dataset
    KMeans(n_clusters = 7).fit(massdata)
    endtime = time.time()
    time_used = endtime - starttime
    print('USING TIME %f' % time_used)
    
# ANALYSIS

    
    def divisionAnalysis(lst):  # count the number of matches of different league divisions
        EPL = 0
        Ligue_1 = 0
        La_Liga = 0
        Serie_A = 0
        Bundesliga = 0
        for div in lst:
            if div == 'EPL':
                EPL += 1
            elif div == 'Ligue_1':
                Ligue_1 += 1
            elif div == 'La_Liga':
                La_Liga += 1
            elif div == 'Serie_A':
                Serie_A += 1
            else:
                Bundesliga += 1
#        print('EPL : %d' % EPL)
#        print('Ligue_1 : %d' % Ligue_1)
#        print('La_Liga : %d' % La_Liga)
#        print('Serie_A : %d' % Serie_A)
#        print('Bundesliga : %d' % Bundesliga)
        return [EPL,Ligue_1,La_Liga,Serie_A,Bundesliga]

    # total proportion of 5 leagues
    proportion = [i/float(np.sum(divisionAnalysis(division))) for i in divisionAnalysis(division)]
    
    # analyse the proportion of 5 divisions in a brunch
        # the input is a list of league names
    def proportionAnalysis(lst):
        # adjust the number according to original proportion
        lstAna = divisionAnalysis(lst)
        lstProportion = []
        for i in range(5):
            lstProportion.append(lstAna[i]/proportion[i])
        
        # change adjusted number to proportion
        Sum = np.sum(lstProportion)
        for league in range(5):
            lstProportion[league] /= Sum
        
        return lstProportion
            
    
    def meanData(lst):  # get average data of the group
        lst = np.array(lst)
        mean = []
        size = np.shape(lst)[1]
        for i in range(size):
            mean.append(lst[:,i].mean())
        return mean
        
        
    
        
        