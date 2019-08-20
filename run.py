import json
import copy
import jsonpickle
from math import *
from student import *

EPS = 0.0000001
total = 1

# index: Index of dividing feature
def divCrossEntropy(dataSet, index):
    numEntries = len(dataSet)
    featCount = 0
    for item in dataSet:
        if item.keys[index] is True:
            featCount += 1
    return (featCount*log(featCount + EPS)+(numEntries-featCount)*log(numEntries-featCount + EPS)), featCount

def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0].keys)
    bestEntropy = inf; bestFeature = -1; bestCnt = 0
    for i in range(numFeatures):
        newEntropy, cnt = divCrossEntropy(dataSet, i)
        if(newEntropy < bestEntropy):
            bestEntropy = newEntropy
            bestFeature = i
            bestCnt = cnt
    return bestFeature, bestCnt

def splitDataSet(dataSet, axis, value):
    retDataSet = []
    featCount = len(dataSet[0].keys) - 1
    for featVec in dataSet:
        if featVec.keys[axis] == value:
            reducedFeatVec = student(0, name=featVec.name)
            reducedFeatVec.keys = featVec.keys[:axis]
            reducedFeatVec.keys.extend(featVec.keys[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet

def createTree(dataSet, labels, keys, depth=0):
    if(depth>10):
        return dataSet
    if len(dataSet) < total/10:
        return dataSet
    bestFeat, bestCnt = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    
    if bestCnt==0 or bestCnt==len(dataSet):
        # All features are same, going deeper is meaningless
        return dataSet
    else:
        keys.append(bestFeatLabel)

    myTree = {bestFeatLabel: {}}
    del(labels[bestFeat])
    uniqueVals = [True, False]
    for value in uniqueVals:
        subLabels = labels[:]
        splitted = splitDataSet(dataSet, bestFeat, value)
        if(len(splitted) > 0):
            myTree[bestFeatLabel][value] = createTree(splitted, subLabels, keys, depth=depth+1)
    return myTree


def read(file):
    with open(file, 'r', encoding='utf8') as f:
        data = json.load(f)
    students = data["students"]
    classes = []
    for item in students.keys():
        classes.extend(students[item])
    classUnique = set(classes)
    classUnique = list(sorted(classUnique))
    
    retStudents = []

    ind = 0
    for item in students.keys():
        ind += 1
        newStudent = student(len(classUnique), name='Student #'+str(ind))
        for cl in students[item]:
            newStudent.keys[classUnique.index(cl)] = True
        newStudent.keysOriginal = students[item]
        retStudents.append(newStudent)
    return retStudents, classUnique, data["subjects"]

if __name__ == '__main__':
    data, labels, subs = read('data2.json')
    [print(item) for item in data]
    total = len(data)
    print(labels)
    print(subs)

    # 'Key' labels used for decision in the tree
    keyLabels = []
    myTree = createTree(data, labels, keyLabels)
    # Items in keyLables are not unique; make a set out of it.
    keyLabelsUnique = sorted(set(keyLabels))

    for key in keyLabelsUnique:
        print(subs[str(key)])

    open('mytree.json','w').write(jsonpickle.encode(myTree))
    open('labels.json','w').write(jsonpickle.encode(labels))
    open('keyLabels.json','w').write(jsonpickle.encode(keyLabelsUnique))

    