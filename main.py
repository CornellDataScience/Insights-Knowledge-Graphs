import subprocess
from predicate_mapping.generate_ids import create_id_files
from predicate_mapping.combine_relations import reduce_relations, heat_map
from predicate_mapping.create_json import to_json

def tuple2json():
    tuplefile = './data/relation_tuples.txt'
    ridfile = './data/relation2id.txt'
    eidfile = './data/entity2id.txt'
    rvecfile = './data/relation2vec.csv'
    thresh = 0.22

    create_id_files(tuplefile, ridfile, eidfile)
    subprocess.call(['./embeddings/Train_TransE'])
    reduce_relations(ridfile, rvecfile, thresh, './data/combined_relations.txt')
    heat_map(ridfile, rvecfile, thresh, './data/relation_heat_map.png')
    to_json(eidfile, tuplefile, './viz/relations.json')

def main(url):
    tuple2json()