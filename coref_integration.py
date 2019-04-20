import ast

relations_file = 'relation_tuples.txt'
coref_file = 'coreference_output.txt'
clusters_file = 'clusters.txt'

# Extract coreference data
with open(coref_file) as f:
    coref = ast.literal_eval(f.read())
    spans = coref['top_spans']
    clusters = coref['clusters']
    text = coref['document']

# Create clusters file as a dictionary
open(clusters_file, mode = 'w').close()
with open(clusters_file, mode = 'a') as f:
    for equivalence_class in range(len(clusters)):
        if equivalence_class == 0:
            f.write('{' + f'{equivalence_class}: [')
        else:
            f.write(f', {equivalence_class}: [')

        line = ''
        for index in clusters[equivalence_class]:
            entity = ''
            for i in range(index[0], index[1] + 1):
                entity += text[i] + ' '
            entity = entity.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
            print(f'[{index[0]}, {index[1]}] >> ' + entity)
            line += f"('{entity}',{index}), "
            
        f.write(line[:-2])  # [:-2] to remove trailing comma and space
        f.write(']')
    f.write('}')