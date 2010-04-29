from pybrain.structure          import FeedForwardNetwork
from pybrain.structure          import LinearLayer, SigmoidLayer
from pybrain.structure          import FullConnection

from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer

from scipy import diag, arange, meshgrid, where
from numpy.random import multivariate_normal


#train [(CellObject, classification),...]

#means = [(-1,0),(2,4),(3,1)]
#cov = [diag([1,1]), diag([0.5,1.2]), diag([1.5,0.7])]
#alldata = ClassificationDataSet(2, 1, nb_classes=3)
#for n in xrange(400):
#    for klass in range(3):
#        input = multivariate_normal(means[klass],cov[klass])
#        alldata.addSample(input, [klass])

alldata = ClassificationDataSet(3,class_labels=["False","True"])

alldata.addSample([1,0,0],[0])
alldata.addSample([1,0,1],[0])
alldata.addSample([1,1,0],[0])
alldata.addSample([1,1,1],[1])
alldata.addSample([1,0,0],[0])
alldata.addSample([1,0,1],[0])
alldata.addSample([1,1,1],[1])
alldata.addSample([0,0,0],[0])

print "allData: "
for data in alldata:
    print data,
print

tstdata, trndata = alldata.splitWithProportion(0.25)

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
outLayer = LinearLayer(trndata.outdim)

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

print "Activate[1,1,1] = " , fnn.activate([1,1,1])
print "Activate[0,0,0] = " , fnn.activate([0,0,0])

trainer = BackpropTrainer( fnn, dataset=trndata, momentum=0.1, verbose=True, weightdecay=0.01)

trainer.trainUntilConvergence(verbose=True)

#for trainIteration in xrange(1):
#    trainer.trainEpochs(5)

print "params"
print fnn.params

print "Activate[1,1,1] = " , fnn.activate([1,1,1])
print "Activate[0,0,0] = " , fnn.activate([0,0,0])