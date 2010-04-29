from pybrain.structure          import FeedForwardNetwork
from pybrain.structure          import LinearLayer, SigmoidLayer
from pybrain.structure          import FullConnection

from pybrain.datasets            import ClassificationDataSet
from pybrain.supervised.trainers import BackpropTrainer

from cell import Cell
from cell import COLOR_LIST, OUTER_SHAPE_LIST, INNER_SHAPE_LIST, ROT_DIRECTION_LIST

import random

KLASS_ARR= [0,0,0]

cellList=[(Cell(),random.randint(0,2)) for i in xrange(20)]

celldata = ClassificationDataSet(5,target=3,class_labels=["Food","Target","Enemy"])

for cell in cellList:
    outerShape=OUTER_SHAPE_LIST.index(cell[0].outerShape)
    outerColor=COLOR_LIST.index((cell[0].outerColor,cell[0].outerColorList))
    outerRotation=ROT_DIRECTION_LIST.index((cell[0].outerRotation,cell[0].outerRotationVal))
    innerShape=INNER_SHAPE_LIST.index(cell[0].innerShape)
    if cell[0].innerColor=="Black":
        innerColor=3
    else:
        innerColor=COLOR_LIST.index((cell[0].innerColor,cell[0].innerColorList))

    klass = KLASS_ARR
    klass[cell[1]]=1

    celldata.addSample([outerShape,outerColor,outerRotation,innerShape,innerColor],klass)

print "cellData: "
for cell in celldata:
    print cell,
print

tstdata, trndata = celldata.splitWithProportion(0.25)

print "Test Data ", tstdata
print "Training Data ", trndata

#trndata._convertToOneOfMany()
#tstdata._convertToOneOfMany()

print "Number of training patterns: ", len(trndata)
print "Input and output dimensions: ", trndata.indim, trndata.outdim
print "input,       target, class):"

fnn = FeedForwardNetwork()

inLayer = LinearLayer(trndata.indim)
hiddenLayer = SigmoidLayer(5)
outLayer = SigmoidLayer(trndata.outdim)

fnn.addInputModule(inLayer)
fnn.addModule(hiddenLayer)
fnn.addOutputModule(outLayer)

in_to_hidden = FullConnection(inLayer, hiddenLayer)
hidden_to_out = FullConnection(hiddenLayer, outLayer)

fnn.addConnection(in_to_hidden)
fnn.addConnection(hidden_to_out)

fnn.sortModules()

print "params"
print fnn.params

trainer = BackpropTrainer( fnn, dataset=trndata, momentum=0.1, verbose=True, weightdecay=0.01)

trainer.trainUntilConvergence(maxEpochs=500,verbose=True)


print "params"
print fnn.params

print "Activate[1,1,1,1,1] = " , fnn.activate([1,1,1,1,1])
print "Activate[0,0,0,0,0] = " , fnn.activate([0,0,0,0,0])