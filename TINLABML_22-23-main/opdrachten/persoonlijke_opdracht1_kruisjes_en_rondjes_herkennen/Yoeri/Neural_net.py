import math
from training_data import training_set, test_set
from classes import Node, Link

def softMax(inVec):
    expVec = [math.exp(inScal) for inScal in inVec]
    aSum = sum(expVec)
    return [expScal/aSum for expScal in expVec]

def costFunc(outVec, modelVec):
    return sum([(lambda x: x*x) (zipped[0] - zipped[1]) for zipped in zip(outVec, modelVec)])  

def compute_average_cost():
    accumulated_cost = 0.0
    
    for trainings_item in training_set:
        for i_row in range(no_of_rows):
            for i_column in range(no_of_columns):
                input_nodes[i_row][i_column].value = trainings_item[0][i_row][i_column]
        accumulated_cost += costFunc(softMax([output_node() for output_node in output_nodes]), symbol_vecs[trainings_item[1]])
    return accumulated_cost / len(training_set)


no_of_rows = 3
no_of_columns = 3

symbol_vecs = {
    '0': (1.0, 0.0),
    'X': (0.0, 1.0),
}

symbol_chars = dict((value, key) for key, value in symbol_vecs.items())

input_nodes = [[Node() for _ in range(no_of_rows)] for _ in range(no_of_columns)]
output_nodes = [Node() for _ in range(2)]

links = []
for in_rows in input_nodes:
    for node in in_rows:
        for out_node in output_nodes:
            links.append(Link(node, out_node))
        

# TRAINING
average_cost = compute_average_cost()
prev_cost = 0.0
weight_change_step = 0.1

while average_cost > 0.01:
    for link in links:
        link.weight += weight_change_step
        prev_cost = average_cost
        average_cost = compute_average_cost()
        if average_cost > prev_cost:
            link.weight -= weight_change_step * 2
            average_cost = compute_average_cost()
            if average_cost > prev_cost:
                link.weight += weight_change_step

print('\n')
print('Training complete. Average cost: ', average_cost)
print('\n')        

# TESTING
for test_item in test_set:
    for i_row in range(no_of_rows):
        for i_column in range(no_of_columns):
            input_nodes[i_row][i_column].value = test_item[i_row][i_column]
    result = (softMax([output_node() for output_node in output_nodes]))
    if result[0] > result[1]:
        print(result, '\t0')
    else:
        print(result, '\tX')