import argparse  #解析命令行参数
import json
import logging  #记录日志信息
import pickle   #序列化
import sys

import torch
from sklearn.metrics import ndcg_score #计算标准化折损累计增益评分（NDCG）
import numpy as np
import torch.nn.functional as F
from scipy import spatial
import torch.multiprocessing as mp
from model import *
from pytictoc import TicToc
#from batching import *
import os.path


def get_type_num():
    type2id = {}
    id2type = {}
    type_counter = 0
    with open("./data/JF17k/entity2prototypes_tt.txt") as entity2type_file:
        for line in entity2type_file:
            splitted_line = line.strip().split("\t")
            entity_type = splitted_line[1]

            if entity_type not in type2id:
                type2id[entity_type] = type_counter
                id2type[type_counter] = entity_type
                type_counter += 1

    entity2type_file.close()
    return type2id, id2type



def main():

    parser = argparse.ArgumentParser(description="Model's hyperparameters")
    parser.add_argument('--num_filters', type = int, default = 200)
    parser.add_argument('--embsize', type = int, default = 100)
    parser.add_argument('--max_neighbor', type = int, default = 12)

    args = parser.parse_args()

    with open("./data/JF17k/dictionaries_and_facts_withGraph.bin", 'rb') as fin:
        data_info = pickle.load(fin)

    train = data_info["train_facts"]
    valid = data_info["valid_facts"]
    test = data_info["test_facts"]
    relation2id = data_info['roles_indexes']
    entity2id = data_info['values_indexes']
    key_val = data_info['role_val']
    BK_graph = data_info['BK_graph']

    id2entity = {}
    for tmpkey in entity2id:
        id2entity[entity2id[tmpkey]] = tmpkey
    id2relation = {}
    for tmpkey in relation2id:
        id2relation[relation2id[tmpkey]] = tmpkey
    n_entities = len(entity2id)
    n_relations = len(relation2id)
    
    type2id, id2type = get_type_num()

    model = imitate_RETA(len(relation2id), len(entity2id), len(type2id) + 1 ,int(args.embsize), 
                         int(args.num_filters), int(args.max_neighbor)).cuda()

if __name__ == "__main__":
    main()