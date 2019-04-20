import ast

relations_file = 'relation_tuples.txt'
coref_file = 'coreference_output.txt'
clusters_file = 'clusters.txt'

with open(coref_file) as f:
    coref = ast.literal_eval(f.read())
    spans = coref['top_spans']
    clusters = coref['clusters']
    text = coref['document']

open(clusters_file, mode = 'w').close()
with open(clusters_file, mode = 'a') as f:
    for equivalence_class in range(len(clusters)):
        if equivalence_class == 0:
            f.write('{' + f'{equivalence_class}: [')
        else:
            f.write(f', {equivalence_class}: [')

        for indicies in clusters[equivalence_class]:
            entity = ''
            for i in range(indicies[0], indicies[1] + 1):
                entity += text[i] + ' '
            entity = entity.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
            print(f'[{indicies[0]}, {indicies[1]}] >> ' + entity)
        
        f.write(']')
    f.write('}')
        

print(type(spans))
print(type(clusters))
print(type(text))