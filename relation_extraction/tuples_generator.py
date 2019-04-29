import ast, re, nltk, json
from allennlp.predictors.predictor import Predictor

# Define file locations
raw_data_file = 'data/raw_data.txt'
relations_file = 'data/relation_tuples.txt'
details_file = 'data/detail_tuples.txt'
coref_file = 'data/coref_tuples.txt'

def create_tuples():
    # Run AllenNLP coreference resolution on raw text
    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz")
    with open(raw_data_file, encoding='UTF-8') as f:
        raw_data = f.read()
    coref = predictor.predict(raw_data)
    clusters = coref['clusters']
    document = coref['document']

    # Create clusters dictionary
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

    # Get text from cluster document
    text = ' '.join(document)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())

    # Run AllenNLP open extraction on text
    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz")
    predictions = [] # stores tuples in the form (prediction, token index)
    index = 0
    for sentence in sentences:
        tokens = sentence.count(' ') + 1
        predictions.append((predictor.predict(sentence), index))
        index += tokens

    # Generate tuples from AllenNLP predictions
    open(relations_file, mode='w').close()
    open(details_file, mode='w').close()
    open(coref_file, mode='w').close()

    for prediction_tuple in predictions:
        prediction, index = prediction_tuple
        for d in prediction['verbs']:
            desc = d['description']
            if '[ARG0: ' in desc and '[V: ' in desc and '[ARG1: ' in desc:                            
                verb_start = desc.find('[V:')
                verb_end = desc.find(']', verb_start)
                verb = desc[verb_start + 4 : verb_end]

                # Create relation tuples
                relations_arg0 = desc[desc.find('[ARG0: ') + 7 : desc.find(']', desc.find('[ARG0: '))].replace(r' ,', r',')
                relations_arg1 = desc[desc.find('[ARG1: ') + 7 : desc.find(']', desc.find('[ARG1: '))].replace(r' ,', r',')

                # Remove tuples with non-noun entities
                pos0 = [token[1] for token in nltk.pos_tag(nltk.tokenize.word_tokenize(relations_arg0))]
                pos1 = [token[1] for token in nltk.pos_tag(nltk.tokenize.word_tokenize(relations_arg1))]
                if 'VB' in pos0[0] or 'VB' in pos1[0]:  # Entity starts with a verb
                    continue

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
                
                # Create coreference tuples
                # TODO: check second index
                coref_arg0_index = index + desc[:desc.find('[ARG0: ')].count(' ')
                coref_arg0_tokens = desc[desc.find('[ARG0: ') + 7 : desc.find(']', desc.find('[ARG0: '))].count(' ') + 1
                coref_arg1_index = index + desc[:desc.find('[ARG1: ')].count(' ') - 2
                coref_arg1_tokens = desc[desc.find('[ARG1: ') + 7 : desc.find(']', desc.find('[ARG1: '))].count(' ') + 1

                coref_arg0_replacements = set()
                coref_arg0_replace_freq = 0
                coref_arg1_replacements = set()
                coref_arg1_replace_freq = 0
                for i in range(coref_arg0_tokens):
                    representative = clusters_dictionary.get(equivalence_dictionary.get(indicies_dictionary.get(coref_arg0_index + i)))
                    if representative != None: 
                        coref_arg0_replace_freq += 1
                        if representative not in coref_arg0_replacements:
                            coref_arg0_replacements.add(representative)
                for i in range(coref_arg1_tokens):
                    representative = clusters_dictionary.get(equivalence_dictionary.get(indicies_dictionary.get(coref_arg1_index + i)))
                    if representative != None: 
                        coref_arg1_replace_freq += 1
                        if representative not in coref_arg1_replacements:
                            coref_arg1_replacements.add(representative)

                coref_arg0 = relations_arg0
                coref_arg1 = relations_arg1

                # Replace string if it contains a single replaceable entity which represents more than half of the tokens in the string
                if len(coref_arg0_replacements) == 1:
                    if coref_arg0_replace_freq / coref_arg0_tokens >= 0.5:
                        coref_arg0 = coref_arg0_replacements.pop()
                if len(coref_arg1_replacements) == 1:
                    if coref_arg1_replace_freq / coref_arg1_tokens >= 0.5:
                        coref_arg1 = coref_arg1_replacements.pop()

                #print(f'[0] {relations_arg0} >> {coref_arg0}: {coref_arg0_replace_freq / coref_arg0_tokens}')
                #print(f'[1] {relations_arg1} >> {coref_arg1}: {coref_arg1_replace_freq / coref_arg1_tokens}')

                # Clean text
                relations_arg0 = relations_arg0.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                relations_arg1 = relations_arg1.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                details_arg0 = details_arg0.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                details_arg1 = details_arg1.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                coref_arg0 = coref_arg0.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                coref_arg1 = coref_arg1.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')

                # Kevin hates spaces
                relations_arg0 = relations_arg0.replace(' ', '_')
                relations_arg1 = relations_arg1.replace(' ', '_')
                details_arg0 = details_arg0.replace(' ', '_')
                details_arg1 = details_arg1.replace(' ', '_')
                coref_arg0 = coref_arg0.replace(' ', '_')
                coref_arg1 = coref_arg1.replace(' ', '_')

                # Write tuples to file
                tuples_delimiter = '\t'
                with open(relations_file, mode='a', encoding='UTF-8') as f:
                    f.write(f'{relations_arg0}{tuples_delimiter}{relations_arg1}{tuples_delimiter}{verb}\n')
                with open(details_file, mode='a', encoding='UTF-8') as f:
                    f.write(f'{details_arg0}{tuples_delimiter}{details_arg1}{tuples_delimiter}{verb}\n')
                with open(coref_file, mode='a', encoding='UTF-8') as f:
                    f.write(f'{coref_arg0}{tuples_delimiter}{coref_arg1}{tuples_delimiter}{verb}\n')

    print('DONE')

if __name__ == '__main__':
    create_tuples()