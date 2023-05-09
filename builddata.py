import tensorflow as tf
import numpy as np
import pickle
import time

ISOTIMEFORMAT = '%Y-%m-%d %X'

tf.compat.v1.flags.DEFINE_string("data_dir", "./data/JF17k", "The data dir.")
tf.compat.v1.flags.DEFINE_string("bin_postfix", "_withGraph", "The new_postfix for the output bin file.")

FLAGS = tf.compat.v1.flags.FLAGS
import sys

FLAGS(sys.argv)




def permutations(arr, postion, end, res):
    if postion == end:
        res.append(tuple(arr))
    else:
        for idx in range(postion, end):
            arr[idx], arr[postion] = arr[postion], arr[idx]
            permutations(arr, postion + 1, end, res)
            arr[idx], arr[postion] = arr[postion], arr[idx]
    
    return res


def load_data_from_txt(filenames, values_indexes = None, roles_indexes = None, ary_permutation = None, BK_graph = None):

    if values_indexes is None :
        values_indexes = dict()
        values = set()
    else:
        values = set(values_indexes)
    
    if roles_indexes is None :
        roles_indexes = dict()
        roles = set()
    else:
        roles = set(values_indexes)
    
    if ary_permutation is None:
        ary_permutation = dict()
    
    if BK_graph is None:
        BK_graph = dict()
    
    max_n = 2
    for filename in filenames:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                xx_dict = eval(line)
                xx = xx_dict['N']
                xx = max(max_n, xx)
    
    data = []
    for i in range(max_n - 1):
        data.append(dict())
    
    
    for filename in filenames:
        with open(filename) as f:
            lines = f.readlines()

        for _, line in enumerate(lines):
            aline = ()
            xx_dict = eval(line)

            for k in xx_dict:
                if k == 'N':
                    continue
                
                if k in roles:
                    role_ind = roles_indexes[k]
                else:
                    roles.add(k)
                    roles_indexes[k] = len(roles) - 1
                    role_ind = roles_indexes[k]
                
                if type(xx_dict[k]) == str:
                    val = xx_dict[k]
                    if val in values:
                        val_ind = values_indexes[val]
                    else:
                        values.add(val)
                        values_indexes[val] = len(values) - 1
                        val_ind = values_indexes[val] 
                    aline = aline + (role_ind,) 
                    aline = aline + (val_ind,)
                else:
                    for num, val in enumerate(xx_dict[k]):
                        if val in values:
                            val_ind = values_indexes[val]
                        else:
                            values.add(val)
                            values_indexes[val] = len(values) - 1
                            val_ind = values_indexes[val] 
                        aline = aline + (role_ind,) 
                        aline = aline + (val_ind,)
                        if val_ind not in BK_graph:
                            BK_graph[val_ind] =[]
                        if num == 0:
                            head_id = val_ind
                        elif num ==1:
                            BK_graph[head_id].append((role_ind, val_ind))

        
            data[xx_dict['N'] - 2][aline] = [1]

    return data, values_indexes, roles_indexes, ary_permutation, BK_graph

def get_neg_candidate_set(folder, values_indexes, roles_indexes):
    role_val ={}
    with open(folder + 'n-ary_train.json') as f:
        lines = f.readlines()
    
    for _, line in enumerate(lines):
        n_dict = eval(line)
        for k in n_dict:
            if k == 'N':
                continue
            k_ind = roles_indexes[k]
            if k_ind not in role_val:
                role_val[k_ind] = []
            v = n_dict[k]
            if type(v) == str:
                v_ind = values_indexes[v]
                if v_ind not in role_val[k_ind]:
                    role_val[k_ind].append(v_ind)
            else:  # Multiple values
                for val in v:
                    val_ind = values_indexes[val]
                    if val_ind not in role_val[k_ind]:
                        role_val[k_ind].append(val_ind)
    return role_val



def build_data(folder='data/'):
    """
    Build data and save to files
    """
    train_facts, values_indexes, roles_indexes, ary_permutation, BK_graph = load_data_from_txt([folder + 'n-ary_train.json'])
    valid_facts, values_indexes, roles_indexes, ary_permutation, BK_graph = load_data_from_txt([folder + 'n-ary_valid.json'],
                                                                                     values_indexes=values_indexes,
                                                                                     roles_indexes=roles_indexes,
                                                                                     ary_permutation=ary_permutation,
                                                                                              BK_graph=BK_graph)
    test_facts, values_indexes, roles_indexes, ary_permutation, BK_graph = load_data_from_txt([folder + 'n-ary_test.json'],
                                                                                    values_indexes=values_indexes,
                                                                                    roles_indexes=roles_indexes,
                                                                                    ary_permutation=ary_permutation,
                                                                                             BK_graph=BK_graph)
    # no_neighbor = []
    # for key in BK_graph.keys():
    #     if len(BK_graph[key]) == 0:
    #         no_neighbor.append(key)
    # print("entities who have no neighbor:{}".format(no_neighbor))
    data_info = {"train_facts": train_facts, "valid_facts": valid_facts, 'test_facts': test_facts,
                 'values_indexes': values_indexes, 'roles_indexes': roles_indexes, 'BK_graph': BK_graph}
    print(values_indexes)
    role_val = get_neg_candidate_set(folder, values_indexes, roles_indexes)
    data_info['role_val'] = role_val
    with open(folder + "/dictionaries_and_facts" + FLAGS.bin_postfix + ".bin", 'wb') as f:
        pickle.dump(data_info, f)


if __name__ == '__main__':
    print(time.strftime(ISOTIMEFORMAT, time.localtime()))
    afolder = FLAGS.data_dir + '/'
    build_data(folder=afolder)
    print(time.strftime(ISOTIMEFORMAT, time.localtime()))