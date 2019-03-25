import subprocess, ast, re

def format_sentence(sentence):
    with open('formatted_input.txt', mode = 'a') as f:
        f.write('{"sentence": "' + sentence.rstrip() + '" }\n')

if __name__ == '__main__':
    open('formatted_input.txt', mode = 'w').close
    with open('input.txt', mode = 'r') as input:
        text = input.read()
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())
        for sentence in sentences:
            format_sentence(sentence[:-1])
        
    open('predictions.txt', 'w').close()
    subprocess.call(['predict.sh'], shell = True)
    
    # write tuples
    with open('predictions.txt', mode = 'r') as raw_predictions:
        open('output.txt', mode = 'w').close
        with open('output.txt', mode = 'a') as out:
            line = raw_predictions.readline()
            while line:
                if line.startswith('prediction:'):
                    for d in ast.literal_eval(line[13:])['verbs']:
                        desc = d['description']
                        if '[ARG0: ' in desc and '[V: ' in desc and '[ARG1: ' in desc:
                            arg0 = desc[desc.find('[ARG0: ') + 7 : desc.find(']', desc.find('[ARG0: '))]
                            verb = desc[desc.find('[V: ')    + 4 : desc.find(']', desc.find('[V: '))]
                            arg1 = desc[desc.find('[ARG1: ') + 7 : desc.find(']', desc.find('[ARG1: '))]
                            out.write(f'({arg0},{verb},{arg1})\n')
                line = raw_predictions.readline()