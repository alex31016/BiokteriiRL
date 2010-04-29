from pybrain.structure          import FeedForwardNetwork
from pybrain.structure          import LinearLayer, SigmoidLayer
from pybrain.structure          import FullConnection

from pybrain.datasets            import ClassificationDataSet
from pybrain.supervised.trainers import BackpropTrainer

from cell import COLOR_LIST, OUTER_SHAPE_LIST, INNER_SHAPE_LIST, ROT_DIRECTION_LIST

KLASS_ARR= [0,0,0]
KLASS_LABELS=["Food","Target","Enemy"]
#from cell import Cell
#import random
#cellList=[(Cell(),random.randint(0,2)) for i in xrange(20)] #recibida como parametro


def transform_cell(cell):
    outerShape=OUTER_SHAPE_LIST.index(cell.outerShape)
    outerColor=COLOR_LIST.index((cell.outerColor,cell.outerColorList))
    outerRotation=ROT_DIRECTION_LIST.index((cell.outerRotation,cell.outerRotationVal))
    innerShape=INNER_SHAPE_LIST.index(cell.innerShape)
    if cell.innerColor=="Black":
        innerColor=3
    else:
        innerColor=COLOR_LIST.index((cell.innerColor,cell.innerColorList))

    return [outerShape,outerColor,outerRotation,innerShape,innerColor]

def create_trained_network(trainingSet):
    celldata = ClassificationDataSet(5,target=3,class_labels=KLASS_LABELS)

    for cell in trainingSet:        
        klass = KLASS_ARR
        klass[KLASS_LABELS.index(cell[1])]=1
        celldata.addSample(transform_cell(cell[0]),klass)

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

    return fnn


def test_network(fnn, sample):
    """Recieves a sample list [W,X,Y,Z,..]and returns its activation (evaluation)"""
    return fnn.activate(sample)
