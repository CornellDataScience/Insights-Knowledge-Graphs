import numpy as np
        
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
        outfile.write('\n')
    with open(entityfile, 'w') as outfile:
        outfile.write('\n'.join([entities[i] + "\t" + str(i) for i in range(len(entities))]))
        outfile.write('\n')

if __name__ == '__main__':
    create_id_files('../data/relation_tuples.txt', '../data/relation2id.txt', '../data/entity2id.txt')