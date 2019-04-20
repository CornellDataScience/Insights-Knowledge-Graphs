import subprocess, ast, re
from nltk import pos_tag as tag, word_tokenize as tokenize

input_file = 'raw_data.txt'                     # Contains the raw, scraped text
formatted_input_file = 'formatted_data.txt'     # Sentences formatted in JSON format for AllenNLP to run on
predictions_file = 'predictions.txt'            # Predictions in JSON format produced by AllenNLP script
relations_file = 'relation_tuples.txt'          # Relation tuples generated from AllenNLP predictions
details_file = 'detail_tuples.txt'              # Parallel to relations file and contains the context and details of the sentence

tuples_delimiter = '\t'

def format_sentence(sentence):
    with open(formatted_input_file, mode = 'a') as f:
        f.write('{"sentence": "' + sentence.rstrip() + '" }\n')

if __name__ == '__main__':
    open(formatted_input_file, mode = 'w').close
    with open(input_file, mode = 'r') as input:
        text = input.read()
        text.replace('\t', ' ')
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())
        for sentence in sentences:
            format_sentence(sentence[:])
        
    print('Running prediction script...')
    open(predictions_file, 'w').close()
    subprocess.call(['predict.sh'], shell = True)
    
    # write tuples
    with open(predictions_file, mode = 'r') as raw_predictions:
        open(relations_file, mode = 'w').close
        open(details_file, mode = 'w').close
        relations = open(relations_file, mode = 'a')
        details = open(details_file, mode = 'a')

        line = raw_predictions.readline()
        while line:
            if line.startswith('prediction:'):
                for d in ast.literal_eval(line[13:])['verbs']:
                    desc = d['description']
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
                        pos_verb = tag(tokenize(verb))
                        # print(verb, pos_verb)

                        relations_arg0 = relations_arg0.replace(' ', '_')
                        relations_arg1 = relations_arg1.replace(' ', '_')
                        details_arg0 = details_arg0.replace(' ', '_')
                        details_arg1 = details_arg1.replace(' ', '_')
                        verb = verb.replace(' ', '_')

                        relations.write(f'{relations_arg0}{tuples_delimiter}{relations_arg1}{tuples_delimiter}{verb}\n')
                        details.write(f'{details_arg0}{tuples_delimiter}{details_arg1}{tuples_delimiter}{verb}\n')

            line = raw_predictions.readline()

        relations.close()
        details.close()

    print('Done')