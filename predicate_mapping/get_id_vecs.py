import numpy as np

def get_ids(idfile):
    with open(idfile, 'r') as infile:
        lines = infile.read().split('\n')[:-1]
        ilist = [''] * len(lines)
        for pair in lines:
            p = pair.split('\t')
            ilist[int(p[1])] = p[0]
    return ilist
    
def get_vectors(vecfile):
    with open(vecfile, 'r') as infile:
        lines = infile.read().split('\n')[:-1]
        vlist = [np.array([float(s) for s in vec.split('\t') if len(s) > 0]) for vec in lines]
    return np.array(vlist)