import ast, re

dir = 'relation extraction'
relations_file = dir + '/relation_tuples.txt'
coref_file = dir + '/coreference_output.txt'
clusters_file = dir + '/clusters.txt'

# Extract coreference data
with open(coref_file) as f:
    coref = ast.literal_eval(f.read())
    spans = coref['top_spans']
    clusters = coref['clusters']
    document = coref['document']

# Create clusters file as a dictionary
open(clusters_file, mode = 'w').close()
with open(clusters_file, mode = 'a') as f:
    for equivalence_class in range(len(clusters)):
        if equivalence_class == 0:
            f.write('{' + f'{equivalence_class}: [')
        else:
            f.write(f', {equivalence_class}: [')

        prediction = ''
        for index in clusters[equivalence_class]:
            entity = ''
            for i in range(index[0], index[1] + 1):
                entity += document[i] + ' '
            entity = entity.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
            prediction += f"('{entity}',{index}), "
            
        f.write(prediction[:-2])  # [:-2] to remove trailing comma and space
        f.write(']')
    f.write('}')

# Get text from cluster document
text = ' '.join(document)
sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())
for sentence in sentences:
    pass
    #sentence = sentence.replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')

# Run AllenNLP open extraction on text
from allennlp.predictors.predictor import Predictor
predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz")

open(dir + '/test.txt', mode = 'w').close()
with open(dir + '/test.txt', mode = 'a') as f:
    predictions = []
    for sentence in sentences:
        predictions.append(predictor.predict(sentence))

# Generate tuples from AllenNLP predictions
for prediction in predictions:
    for d in prediction['verbs']:
        desc = d['description']
        print(desc) # <--- last left off
        break
        if '[ARG0: ' in desc and '[V: ' in desc and '[ARG1: ' in desc:                            
            verb_start = desc.find('[V:')
            verb_end = desc.find(']', verb_start)
            verb = desc[verb_start + 4 : verb_end]

            relations_arg0 = desc[desc.find('[ARG0: ') + 7 : desc.find(']', desc.find('[ARG0: '))].replace(r' ,', r',')
            relations_arg1 = desc[desc.find('[ARG1: ') + 7 : desc.find(']', desc.find('[ARG1: '))].replace(r' ,', r',')

            details_arg0 = desc[:verb_start]
            details_arg1 = desc[verb_end + 1:]

            while '[ARG' in details_arg0:
                i = details_arg0.find('[ARG')
                j = details_arg0.find(']', i)
                details_arg0 = details_arg0[:i] + details_arg0[i+7:j] + details_arg0[j+1:]

            while '[ARG' in details_arg1:
                i = details_arg1.find('[ARG')
                j = details_arg1.find(']', i)
                details_arg1 = details_arg1[:i] + details_arg1[i+7:j] + details_arg1[j+1:]

            details_arg0 = details_arg0.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
            details_arg1 = details_arg1.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                                
            # TODO: remove tuples with bad entities using POS tagger
            # pos_verb = tag(tokenize(verb))
            # print(verb, pos_verb)

            #relations_arg0 = relations_arg0.replace(' ', '_')
            #relations_arg1 = relations_arg1.replace(' ', '_')
            #details_arg0 = details_arg0.replace(' ', '_')
            #details_arg1 = details_arg1.replace(' ', '_')
            #verb = verb.replace(' ', '_')

            tuples_delimiter = ','
            print(f'({relations_arg0}{tuples_delimiter}{verb}{tuples_delimiter}{relations_arg1})\n')
            #print(f'({details_arg0}{tuples_delimiter}{verb}{tuples_delimiter}{details_arg1})\n')



print('DONE')