import tensorflow as tf
import numpy as np
import pickle
import time


def load_data_from_txt(filenames):
    
    with open(filenames, 'r') as f:
        for line in f:
            print(line)


load_data_from_txt('data/JF17K/n-ary_train.json')