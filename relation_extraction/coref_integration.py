import ast, re, nltk, json

data_dir = 'relation_extraction'
relations_file = data_dir + '/relation_tuples.txt'
details_file = data_dir + '/detail_tuples.txt'
coref_file = data_dir + '/coref_tuples.txt'
coref_input_file = data_dir + '/coreference_output.txt'
clusters_file = data_dir + '/clusters.txt'

# Extract coreference data
with open(coref_input_file) as f:
    coref = ast.literal_eval(f.read())
    spans = coref['top_spans']
    clusters = coref['clusters']
    document = coref['document']

# Create clusters dictionary
open(clusters_file, mode = 'w').close()
with open(clusters_file, mode = 'a') as f:
    indicies_dictionary = {} # key = index (ex. 11), value = index range (ex. (11,16))
    equivalence_dictionary = {} # key = index range; value = clusterID
    clusters_dictionary = {} # key = clusterID, value = most representative entity
    for equivalence_class in range(len(clusters)):
        equivalent_entities = []
        for index_range in clusters[equivalence_class]:
            index_range = tuple(index_range)
            entity = ''
            for i in range(index_range[0], index_range[1] + 1):
                entity += document[i] + ' '
                indicies_dictionary[i] = index_range
            entity = entity.strip()#.replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
            equivalence_dictionary[index_range] = equivalence_class
            equivalent_entities.append(entity)

        # Sort equivalent_entities in decreasing frequency and delete duplicates
        entities = []
        freq = []
        for i in range(len(equivalent_entities)):
            flag = True
            for j in range(len(entities)):
                if equivalent_entities[i].upper() == entities[j].upper():
                    freq[j] += 1
                    flag = False
                    break
            if flag:
                entities.append(equivalent_entities[i])
                freq.append(1)
        equivalent_entities = []
        for _ in range(len(entities)):
            index = freq.index(max(freq))
            freq.pop(index)
            equivalent_entities.append(entities.pop(index))

        # Pick most frequent entity that isn't a pronoun as the most representative entity
        representative_entity = equivalent_entities.pop(0)
        pos = nltk.pos_tag(nltk.tokenize.word_tokenize(representative_entity))[0][1]
        while len(equivalent_entities) > 0 and 'PRP' in pos:
            representative_entity = equivalent_entities.pop(0)
            pos = nltk.pos_tag(nltk.tokenize.word_tokenize(representative_entity))[0][1]           
        clusters_dictionary[equivalence_class] = representative_entity
        
    json.dump(clusters_dictionary, f)

# Get text from cluster document
text = ' '.join(document)
sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())
# sentence = sentence.replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')

# Run AllenNLP open extraction on text
from allennlp.predictors.predictor import Predictor
predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz")
predictions = [] # stores tuples in the form (prediction, token index, tokens in sentence)
index = 0
for sentence in sentences:
    tokens = sentence.count(' ') + 1
    predictions.append((predictor.predict(sentence), index, tokens))
    index += tokens

# Generate tuples from AllenNLP predictions
open(relations_file, mode='w').close()
open(details_file, mode='w').close()
open(coref_file, mode='w').close()

for prediction_tuple in predictions:
    prediction, index, tokens = prediction_tuple
    for d in prediction['verbs']:
        desc = d['description']
        print(f'{desc}, {index}, {tokens}')

        if '[ARG0: ' in desc and '[V: ' in desc and '[ARG1: ' in desc:                            
            verb_start = desc.find('[V:')
            verb_end = desc.find(']', verb_start)
            verb = desc[verb_start + 4 : verb_end]

            # Create relation tuples
            relations_arg0 = desc[desc.find('[ARG0: ') + 7 : desc.find(']', desc.find('[ARG0: '))].replace(r' ,', r',')
            relations_arg1 = desc[desc.find('[ARG1: ') + 7 : desc.find(']', desc.find('[ARG1: '))].replace(r' ,', r',')

            # Create detail tuples
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
            
            # Create coreference tuples
            coref_arg0_index = index + desc[:desc.find('[ARG0: ')].count(' ')
            coref_arg0_tokens = desc[desc.find('[ARG0: ') + 7 : desc.find(']', desc.find('[ARG0: '))].count(' ') + 1
            coref_arg1_index = index + desc[:desc.find('[ARG1: ')].count(' ') - 2
            coref_arg1_tokens = desc[desc.find('[ARG1: ') + 7 : desc.find(']', desc.find('[ARG1: '))].count(' ') + 1

            print(f'{relations_arg0}, {verb}, {relations_arg1}')
            print(f'{coref_arg0_index}, size {coref_arg0_tokens}; {coref_arg1_index}, size {coref_arg1_tokens}')
            
            coref_arg0 = equivalence_dictionary.get(indicies_dictionary.get(coref_arg0_index))
            coref_arg1 = equivalence_dictionary.get(indicies_dictionary.get(coref_arg0_index))

            # TODO: remove tuples with bad entities using POS tagger
            # pos_verb = tag(tokenize(verb))
            # print(verb, pos_verb)

            #relations_arg0 = relations_arg0.replace(' ', '_')
            #relations_arg1 = relations_arg1.replace(' ', '_')
            #details_arg0 = details_arg0.replace(' ', '_')
            #details_arg1 = details_arg1.replace(' ', '_')
            #verb = verb.replace(' ', '_')

            tuples_delimiter = ','
            with open(relations_file, mode='a') as f:
                f.write(f'({relations_arg0}{tuples_delimiter}{verb}{tuples_delimiter}{relations_arg1})\n')
            with open(details_file, mode='a') as f:
                f.write(f'({details_arg0}{tuples_delimiter}{verb}{tuples_delimiter}{details_arg1})\n')
            with open(coref_file, mode='a') as f:
                f.write(f'({coref_arg0}{tuples_delimiter}{verb}{tuples_delimiter}{coref_arg1})\n')


print('DONE')