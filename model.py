import json
import pickle

import torch, math, itertools, os              #由于这个包貌似不支持python3.9，好像也没有被使用，所以注释一下先, psutil，主要作用是监控系统资源
from torch.nn import functional as F, Parameter
from torch.autograd import Variable
from itertools import permutations, product
from collections import defaultdict
from torch.nn.init import xavier_normal_, xavier_uniform_, uniform_, zeros_
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
import numpy as np
import random
import copy
import logging

class imitate_RETA(torch.nn.Module):
    def __init__(self, num_relations, num_entities, num_types, embedding_size, num_filters, max_neighbor):
        super().__init__()
        self.num_relations = num_relations
        self.num_entities = num_entities
        self.embedding_size = embedding_size
        self.num_filters = num_filters
        self.max_neighbor = max_neighbor
        self.num_types = num_types
        self.weight = 2
        
        self.emb_relations = torch.nn.Embedding(self.num_relations, self.embedding_size, padding_idx = 0)
        self.emb_entities = torch.nn.Embedding(self.num_entities, self.embedding_size, padding_idx = 0)
        self.emb_types = torch.nn.Embedding(self.num_types, self.embedding_size, padding_idx = 0)


        self.Conv1 = torch.nn.Conv2d(1, self.num_filters, (3, 3))
        self.Conv2 = torch.nn.Conv2d(1, self.num_filters, (3, 3))

         self.f_FCN_net = torch.nn.Linear((num_filters * (embedding_size - 2)) * 2, 1)
