from numpy import exp, array, dot, random as nrandom, vectorize
import numpy
import json
class NeuralNetwork:

    # todo : document what a,b,c are
    def __init__(self, a, b = None, c = None, wih = None, who = None, bh = None, bo = None):
        numpy.seterr(all='ignore')
        if isinstance(a, NeuralNetwork):
            self.input_nodes = a.input_nodes
            self.hidden_nodes = a.hidden_nodes
            self.output_nodes = a.output_nodes

            self.weight_ih = a.weight_ih.copy()
            self.weight_ho = a.weight_ho.copy()
            self.bias_h = a.bias_h.copy()
            self.bias_o = a.bias_o.copy()

        else:
            self.input_nodes = a
            self.hidden_nodes = b
            self.output_nodes = c

            # initialize a matrice for weights between INPUTS and HIDDEN layer:
            if wih is not None and len(wih) > 0 : 
                self.weight_ih = wih
            else:
                # 2 * Random - 1 enable to have a number into [-1, 1]
                self.weight_ih = 2 * nrandom.random((self.hidden_nodes,self.input_nodes)) - 1
                
            if who is not None and len(who) > 0 : 
                self.weight_ho = who
            else:
                # initialize a matrice for weights between HIDDEN and OUTPUTS layer:
                self.weight_ho = 2 * nrandom.random((self.output_nodes, self.hidden_nodes)) - 1

            if bh is not None and len(bh) > 0 : 
                self.bias_h = bh
            else:
                # initialize a matrice for biais for the HIDDEN layer:
                self.bias_h = 2 * nrandom.random((self.hidden_nodes, 1)) - 1

            if bo is not None and len(bo) > 0 : 
                self.bias_o = bo
            else: 
                # initialize a matrice for biais for the OUTPUT layer:
                self.bias_o = 2 * nrandom.random((self.output_nodes, 1)) - 1

        self.learning_rate = 1
        
    def predict(self, inputs):
        inputs = inputs.reshape(self.input_nodes, 1)

        # generating the hidden layer
        hidden = dot(self.weight_ih, inputs)
        hidden += self.bias_h
        # activation function
        hidden = self.sigmoid(hidden)

        # generating the output layer
        outputs = dot(self.weight_ho, hidden )
        outputs += self.bias_o
        # activation function
        outputs = self.sigmoid(outputs)

        return hidden, outputs
        
    def train(self, inputs, target_outputs):
        
        hidden, outputs = self.predict(inputs)
        inputs = inputs.reshape(self.input_nodes, 1)
        target_outputs = target_outputs.reshape(self.output_nodes, 1)

        # Compute delta HIDDEN - OUTPUT
        output_errors = target_outputs - outputs
        output_delta = self.d_sigmoid(outputs)  * output_errors *  self.learning_rate

        # Compute delta INPUT - HIDDEN
        hidden_errors = dot(self.weight_ho.T, output_delta)
        hidden_delta = self.d_sigmoid(hidden) * hidden_errors * self.learning_rate

        # adjust the weight by deltas
        self.weight_ho += dot(output_delta, hidden.T)
        # adjust the bias by its deltas (wich his just the gradient = lr * error * d_sigmoid)
        self.bias_o += output_delta

        # adjust the weight by deltas
        self.weight_ih += dot(hidden_delta, inputs.T)
        # adjust the bias by its deltas (wich his just the gradient = lr * error * d_sigmoid)
        self.bias_h += hidden_delta


    def sigmoid(self, x):
        return 1 / (1 + exp(-x))
    
    def d_sigmoid(self, x):
        # derivative of the sigmoid function
        return x * (1 - x)
    
    def copy(self) :
        return NeuralNetwork(self)

    def mutate(self, rate) :
        def mutate(value) :
            if nrandom.random() <= rate :
                val = nrandom.random() * 2 - 1
                return val
            else :
                return value

        mutateFunc = vectorize(mutate)
        self.weight_ih = mutateFunc(self.weight_ih)
        self.weight_ho = mutateFunc(self.weight_ho)
        self.bias_h = mutateFunc(self.bias_h)
        self.bias_o = mutateFunc(self.bias_o)
    
    def tojson(self):
        result = "{"
        result += "\"input_nodes\" : " + str(self.input_nodes)
        result += ", "
        result += "\"hidden_nodes\" : " + str(self.hidden_nodes)
        result += ", "
        result += "\"output_nodes\" : " + str(self.output_nodes)
        result += ", "
        result += "\"weight_ih\" : " + json.dumps(self.weight_ih.tolist())
        result += ", "
        result += "\"weight_ho\" : " + json.dumps(self.weight_ho.tolist())
        result += ", "
        result += "\"bias_h\" : " + json.dumps(self.bias_h.tolist())
        result += ", "
        result += "\"bias_o\" : " + json.dumps(self.bias_o.tolist())
        result += "}"
        
        return result

    @staticmethod
    def fromjson(jsonTxt) :
        obj = json.loads(jsonTxt)
        input_nodes = obj["input_nodes"]
        hidden_nodes = obj["hidden_nodes"]
        output_nodes = obj["output_nodes"]

        weight_ih = array(obj["weight_ih"])
        weight_ho = array(obj["weight_ho"])
        bias_h = array(obj["bias_h"])
        bias_o = array(obj["bias_o"])

        return NeuralNetwork(input_nodes, hidden_nodes, output_nodes, weight_ih, weight_ho, bias_h, bias_o)

    def __str__(self):
        return "(" +str(self.input_nodes) + ", " + str(self.hidden_nodes) + ", " + str(self.output_nodes) + ")"

class TrainingData(object):
    pass