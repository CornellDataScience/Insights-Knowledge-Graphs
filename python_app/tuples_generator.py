import ast, re, nltk, json
from allennlp.predictors.predictor import Predictor

def main(raw_data):
    # Run AllenNLP coreference resolution on raw text
    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz")
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
    # open(relations_file, mode='w').close()
    # open(details_file, mode='w').close()
    # open(coref_file, mode='w').close()

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
                # TODO: i don't think the second index works right...
                coref_arg0_index = index + desc[:desc.find('[ARG0: ')].count(' ')
                coref_arg0_tokens = desc[desc.find('[ARG0: ') + 7 : desc.find(']', desc.find('[ARG0: '))].count(' ') + 1
                coref_arg1_index = index + desc[:desc.find('[ARG1: ')].count(' ') - 2
                coref_arg1_tokens = desc[desc.find('[ARG1: ') + 7 : desc.find(']', desc.find('[ARG1: '))].count(' ') + 1

                coref_arg0 = coref_arg1 = None
                while coref_arg0 == None and coref_arg0_tokens > 0:
                    coref_arg0 = clusters_dictionary.get(equivalence_dictionary.get(indicies_dictionary.get(coref_arg0_index)))
                    coref_arg0_tokens -= 1
                    coref_arg0_index += 1
                while coref_arg1 == None and coref_arg1_tokens > 0:
                    coref_arg1 = clusters_dictionary.get(equivalence_dictionary.get(indicies_dictionary.get(coref_arg1_index)))
                    coref_arg1_tokens -= 1
                    coref_arg1_index += 1

                if coref_arg0 == None:
                    coref_arg0 = relations_arg0
                if coref_arg1 == None:
                    coref_arg1 = relations_arg1

                # Clean text
                relations_arg0 = relations_arg0.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                relations_arg1 = relations_arg1.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                details_arg0 = details_arg0.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                details_arg1 = details_arg1.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                coref_arg0 = coref_arg0.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')
                coref_arg1 = coref_arg1.strip().replace(r' ,', r',').replace(' .', '.').replace(' \'', '\'').replace(' "', '"').replace(' ;', ';')

                # Write tuples to file
                result = ''
                tuples_delimiter = ','
                result += coref_arg0
                result += tuples_delimiter
                result += verb
                result += tuples_delimiter
                result += coref_arg1
                result += '\n'

    return result