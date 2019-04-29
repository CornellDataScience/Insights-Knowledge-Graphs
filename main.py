import subprocess
import sys
from predicate_mapping.generate_ids import create_id_files
from predicate_mapping.combine_relations import reduce_relations, heat_map
from predicate_mapping.create_json import to_json
from relation_extraction.scrape import read_page
from relation_extraction.tuples_generator import create_tuples

tuplefile = './data/coref_tuples.txt'
ridfile = './data/relation2id.txt'
eidfile = './data/entity2id.txt'
rvecfile = './data/relation2vec.csv'

def tuple2json():
    thresh = 0.22

    create_id_files(tuplefile, ridfile, eidfile)
    subprocess.call(['./embeddings/Train_TransE'])
    heat_map(ridfile, rvecfile, thresh, './data/relation_heat_map.png')
    recombine(thresh)

def recombine(thresh):
    combined_rels = reduce_relations(ridfile, rvecfile, thresh, './data/combined_relations.txt')
    to_json(eidfile, ridfile, tuplefile, combined_rels, './templates/relations.json',)

def main(url):
    #read_page(url)
    create_tuples()
    tuple2json()


if __name__ == '__main__':
    main('https://en.wikipedia.org/wiki/Avengers:_Endgame')