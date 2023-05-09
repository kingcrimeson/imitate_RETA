
import torch
import torch.nn as nn

import pickle 

with open("./data/JF17k/Entity&Type_4.bin", 'rb') as fin:
    data_info = pickle.load(fin)
for key in data_info.keys():
    print(key)
print(type(data_info["type2EM"]))
print(type(data_info["point2typeList"]))
print(type(data_info["type2entity"]))