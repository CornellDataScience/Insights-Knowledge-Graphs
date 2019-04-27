import json
from get_id_vecs import get_ids

def to_json(eidfile, triplefile, jsonfile):
    jsondict = {"nodes": [], "links": []}
    entities = get_ids(eidfile)
    
    for i in range(len(entities)):
        jsondict["nodes"].append({"id": i, "name": entities[i]})
        
    with open(triplefile, 'r') as infile:
        for line in infile.read().split('\n'):
            if line == '':
                continue
            triple = line.split('\t')
            jsondict["links"].append({"source": entities.index(triple[0]),"target": entities.index(triple[1]),"name":triple[2]})
    
    with open(jsonfile, 'w') as outfile:
        outfile.write(json.dumps(jsondict))

if __name__ == '__main__':
    to_json('./data/entity2id.txt', './data/relation2id.txt', './viz/relations.json')