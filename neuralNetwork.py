from pybrain.structure          import FeedForwardNetwork
from pybrain.structure          import LinearLayer, SigmoidLayer
from pybrain.structure          import FullConnection

from pybrain.tools.shortcuts     import buildNetwork
from pybrain.structure.modules   import SoftmaxLayer

from pybrain.datasets            import ClassificationDataSet
from pybrain.supervised.trainers import BackpropTrainer

from cell import COLOR_LIST, OUTER_SHAPE_LIST, INNER_SHAPE_LIST, ROT_DIRECTION_LIST

KLASS_LABELS=["Target","Enemy","Food"]
#from cell import Cell
#import random
#cellList=[(Cell(),random.randint(0,2)) for i in xrange(20)] #recibida como parametro


def transform_cell(cell):
    outerShape=generate_input_array(OUTER_SHAPE_LIST,cell.outerShape)
    innerShape=generate_input_array(INNER_SHAPE_LIST,cell.innerShape)
    outerColor=generate_input_array(COLOR_LIST,(cell.outerColor,cell.outerColorList))
    rotation=generate_input_array(ROT_DIRECTION_LIST,(cell.outerRotation,cell.outerRotationVal))

    if cell.innerColor=="Black":
        innerColor=[0,0,0,1]
    else:
        innerColor=generate_input_array(COLOR_LIST+[0],(cell.innerColor,cell.innerColorList)) #has a tiny +[0] patch

    return outerShape+innerShape+outerColor+innerColor+rotation

def generate_input_array(list, carac):
    length=len(list)
    index=list.index(carac)
    array=[0]*length
    
    if index >=length:
        print "@generateInputArray: Index larger than length"
        return array
    array[index]=1
    return array

def create_trained_network(trainingSet):
    length=len(OUTER_SHAPE_LIST)+len(INNER_SHAPE_LIST)+len(COLOR_LIST)*2+1+len(ROT_DIRECTION_LIST) #sigh.... similar tiny +1 patch   u_u
    celldata = ClassificationDataSet(length,target=3,class_labels=KLASS_LABELS)

    for cell in trainingSet:    
        klass = [0,0,0]
        klass[KLASS_LABELS.index(cell[1])]=1

        print "*"*20
        print transform_cell(cell[0])
        print klass

        celldata.addSample(transform_cell(cell[0]),klass)

    print "cellData: "
    for cell in celldata:
        print cell,
    print

    tstdata, trndata = celldata.splitWithProportion(0.25)

    print "Test Data ", tstdata
    print "Training Data ", trndata

    trndata._convertToOneOfMany()
    tstdata._convertToOneOfMany()

    print "Number of training patterns: ", len(trndata)
    print "Input and output dimensions: ", trndata.indim, trndata.outdim
    print "input,       target, class):"

#    fnn = FeedForwardNetwork()
#
#    inLayer = SigmoidLayer(trndata.indim)
#    hiddenLayer = SigmoidLayer(5)
#    outLayer = LinearLayer(trndata.outdim)
#
#    fnn.addInputModule(inLayer)
#    fnn.addModule(hiddenLayer)
#    fnn.addOutputModule(outLayer)
#
#    in_to_hidden = FullConnection(inLayer, hiddenLayer)
#    hidden_to_out = FullConnection(hiddenLayer, outLayer)
#
#    #in_to_out = FullConnection(inLayer,outLayer)
#
#    fnn.addConnection(in_to_hidden)
#    fnn.addConnection(hidden_to_out)
#
#    #fnn.addConnection(in_to_out)
#
#    fnn.sortModules()


    fnn = buildNetwork(trndata.indim, 5, trndata.outdim, outclass=SoftmaxLayer)

    print "params"
    print fnn.params

    trainer = BackpropTrainer( fnn, dataset=trndata, momentum=0.1, verbose=True, weightdecay=0.01)

    trainer.trainUntilConvergence(maxEpochs=5000,verbose=True)


    print "params"
    print fnn.params

    return fnn


def test_network(fnn, sample):
    """Recieves a sample list [W,X,Y,Z,..]and returns its activation (evaluation)"""
    return fnn.activate(sample)
