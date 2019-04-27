import numpy as np

def get_ids(idfile):
    with open(idfile, 'r') as infile:
        lines = infile.read().split('\n')
        ilist = [''] * len(lines)
        for pair in lines:
            p = pair.split('\t')
            ilist[int(p[1])] = p[0]
    return ilist
    
def get_vectors(vecfile):
    with open(vecfile, 'r') as infile:
        lines = infile.read().split('\n')
        vlist = [np.array([float(s) for s in vec.split('\t') if len(s) > 0]) for vec in lines]
    return np.array(vlist)
        
def create_id_files(triplefile, relationfile, entityfile):
    entities = set()
    relations = set()
    with open(triplefile, 'r') as infile:
        for line in infile.read().split('\n'):
            if line == '':
                continue
            triple = line.split('\t')
            entities.add(triple[0])
            entities.add(triple[1])
            relations.add(triple[2])
    entities = list(entities)
    relations = list(relations)
    with open(relationfile, 'w') as outfile:
        outfile.write('\n'.join([relations[i] + '\t' + str(i) for i in range(len(relations))]))
    with open(entityfile, 'w') as outfile:
        outfile.write('\n'.join([entities[i] + "\t" + str(i) for i in range(len(entities))]))