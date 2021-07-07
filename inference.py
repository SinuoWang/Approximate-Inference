#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import math
from random import *
import sys



class Node:
    def __init__(self):
        self.name = None
        self.parents_num = 0
        self.par_idx_list = []
        self.evidence = False
        self.evidence_val = 9
        self.topo_next_node = None
        self.CPT = []


def create_name_num_dict(rv_names_list):
    name_num_dict = {}
    i = 0
    for name in rv_names_list:
        name_num_dict[name] = i
        i+=1
    return name_num_dict


def create_topological_order_list(graph_table,rv_names_list,name_num_dict):
    topo_list=[]
    par = []
    for i in range(rv_num):
        #find coln all 0, i.e. earliest parents
        if not any([row[i] for row in graph_table]):
            topo_list.append(i)
            par.append(i)
        #print('par: ',par)

    while len(topo_list) < rv_num:
        chil = []
        for p_idx in par:
            for j in range(rv_num):
                if graph_table[p_idx][j] == 1 and name_num_dict[rv_names_list[j]] not in topo_list:
                    topo_list.append(j)
                    chil.append(j)
        #the children will be the parents for next generation
        par=chil
    return topo_list

def find_row(node,state):
    par_num = node.parents_num
    #find the row
    if par_num > 0:
        par_state_list = []
        for idx in node.par_idx_list:
            par_state_list.append(state[idx])
        r_idx = 0

        for i in range(par_num):
            r_idx = r_idx + par_state_list[i]*(2**(par_num-1-i))
        row = node.CPT[r_idx]
    elif par_num == 0:
        row = node.CPT[0]
    float_row = [float(p) for p in row]
    return float_row

def state_update(node,row,state,sample):
    #determine T F, update state
    num = node.number
    sample = random()
    if row[0] < row[1]:
        if sample < row[0]:
            state[num] = 1
        else:
            state[num] = 0

    if row[0] > row[1]:
        if sample < row[1]:
            state[num] = 0
        else:
            state[num] = 1

    #print('sample: ',sample, ',row: ', row)
    #print('result: ',state[num])
    return state


def read_prob(node,state,row):
    #print(type(state))
    if state[node.number] == 1:
        prob = row[0]
    else:
        prob = row[1]
    return prob


def calculate_state_w_dict(node_topo_list):
    state_w_dict = {}
    freq = 0
    for samps in range(100000):
        w=1.0
        w_freq = [w,freq]
        state = [0]*rv_num
        for node in node_topo_list:
            if node.evidence == True:
                state[node.number] = node.evidence_val
                #print(node.evidence_val)
                row = find_row(node,state)
                prob = read_prob(node,state,row)
                #print('prob=',prob)
                w = w*prob
            else:
                row = find_row(node,state)
                state = state_update(node,row,state,sample)
            #print('node num: ', node.number,'---state: ',state,'---row',row)

        state_str = "".join([str(x) for x in state])
        if state_str not in state_w_dict.keys():
            w_freq[0] = w
            w_freq[1] = 1
            #print('w-freq:--------',w_freq)

        else:
            new_arr = state_w_dict[state_str]
            new_arr[1] += 1
            w_freq = new_arr
            #print('!!!!!!!!!!!',state_w_dict[state_str])
        state_w_dict.update({state_str:w_freq})
        #print(state_w_dict)
    return state_w_dict


def calculate_prob(state_w_dict,name_num_dict,query):
    wT_sum = 0
    wF_sum = 0
    alpha = 0
    probability = [wT_sum, wF_sum]
    query_idx = name_num_dict[query]
    #print('query_idx',query_idx)
    #print('-------------------')
    for key in state_w_dict:
        if key[query_idx] == '1':
            wT_sum = wT_sum + state_w_dict[key][0] * state_w_dict[key][1]
            #print('T: ',state_w_dict[key][0],'*',state_w_dict[key][1])
            #print('w',state_w_dict[key][0])
        elif key[query_idx] == '0':
            wF_sum = wF_sum + state_w_dict[key][0] * state_w_dict[key][1]
            #print('F:',state_w_dict[key][0],'*',state_w_dict[key][1])
            #print('w',state_w_dict[key][0])
    alpha = 1/(wT_sum + wF_sum)
    probability = [wT_sum*alpha, wF_sum*alpha]
    return probability



if __name__ == '__main__':
    BN_file_path = sys.argv[1]
    query_file_path = sys.argv[2]

    BN_file = open(BN_file_path)
    query_file = open(query_file_path)

    rv_num = int(BN_file.readline().strip().split()[0])
    #print(rv_num)

    #get rid of blank line
    BN_file.readline()

    #get random variables names in a list
    rv_names_list = BN_file.readline().strip().split()
    #print(rv_names_list)

    #get rid of blank line
    BN_file.readline()

    graph_table=[]
    line=BN_file.readline()
    while line:
        row = [int(val) for val in line.strip().split()]
        graph_table.append(row)
        line=BN_file.readline()
        if len(line.strip()) < 1:
         break
    #print(graph_table)

    name_num_dict = create_name_num_dict(rv_names_list)
    #print(name_num_dict)

    topo_list = create_topological_order_list(graph_table,rv_names_list,name_num_dict)
    #print(topo_list)

    content = query_file.readline()
    content = content.replace("P(", "")
    content = content.replace(")", "")
    content = content.replace("=", " ")
    content = content.split()

    #print(content)
    query = ""
    evidence_list = []
    evidence_val_list = []

    for letter in content:
        if letter == '|':
            break
        else:
            query = letter

    while '|' in content:
        content.pop(0)

    evidence_list = content[::2]
    evidence_val_list = content[1::2]

    for i in range(len(evidence_val_list)):
        if evidence_val_list[i] == 'true,':
            evidence_val_list[i] = 'true'
        if evidence_val_list[i] == 'false,':
            evidence_val_list[i] = 'false'

    state = [0]*rv_num


    for i in range(len(evidence_list)):
        evidence_name = evidence_list[i]
        idx = name_num_dict[evidence_name]
        #print('-----evidence_val_list:', evidence_val_list,'----evidenve val i:',evidence_val_list[i])
        if evidence_val_list[i] == 'true':
            state[idx] = 1
            #print('its true!!!!')
        else:
            state[idx] = 0
    #print('!!!!!!!state:',state)
    #print('evidence_list: ', evidence_list)
    #print('evidence_val_list: ',evidence_val_list)

    #print(query)
    #print(evidence_list)
    #print(evidence_val_list)
    #print(state)


    #create node network
    node_list = []
    for i in range(rv_num):
        node = Node()
        #print(rv_names_list)
        node.name = rv_names_list[i]
        node.number = name_num_dict[node.name]
        if node.name in evidence_list:
            node.evidence = True
            node.evidence_val = state[i]
            #print('state i :',state[i])
        for j in range(rv_num):
            if graph_table[j][i] == 1:
                node.par_idx_list.append(j)
        node.parents_num = len(node.par_idx_list)
        for r in range(2**node.parents_num):
            node.CPT.append(BN_file.readline().strip().split())
        #node.CPT = np.array(node.CPT)
        #print(node.CPT)
        node_list.append(node)
        BN_file.readline() # remove blank line after a CPT

    node_topo_list = []
    for i in topo_list:
        node_topo_list.append(node_list[i])

    state_w_dict = calculate_state_w_dict(node_topo_list)
    probability = calculate_prob(state_w_dict,name_num_dict,query)

    print(probability[0],probability[1])

    #state = [0,1,1,0,0]
    #print(find_row(node_topo_list[2],state))
