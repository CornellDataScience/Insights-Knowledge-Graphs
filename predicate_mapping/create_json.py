import json
import numpy as np
import en_core_web_sm


def get_ids(idfile):
    with open(idfile, 'r') as infile:
        lines = infile.read().split('\n')[:-1]
        ilist = [''] * len(lines)
        for pair in lines:
            p = pair.split('\t')
            ilist[int(p[1])] = p[0]
    return ilist

def to_json(eidfile, ridfile, triplefile, combined_rels, jsonfile):
    jsondict = {"nodes": [], "links": []}
    entities = get_ids(eidfile)
    relations = get_ids(ridfile)

    nlp = en_core_web_sm.load()
    f = lambda x: '#69b3a2' if [token for token in nlp(x) if token.ent_type_ == 'PERSON'] == [] else '#589bdd'
    for i in range(len(entities)):
        jsondict["nodes"].append({"id": i, "name": entities[i].replace('_', ' '), "color": f(entities[i].replace('_', ' '))})
        
    with open(triplefile, 'r') as infile:
        for line in infile.read().split('\n'):
            if line == '':
                continue
            triple = line.split('\t')
            jsondict["links"].append({"source": entities.index(triple[0]),"target": entities.index(triple[1]),"name":combined_rels[relations.index(triple[2])].replace('_', ' ')})
    
    with open(jsonfile, 'w') as outfile:
        outfile.write(json.dumps(jsondict))

def main():
    to_json('./data/entity2id.txt', './data/relation_tuples.txt', './templates/relations.json')

if __name__ == '__main__':
    main()