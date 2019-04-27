import nltk
text = 'his'
pos = nltk.pos_tag(nltk.tokenize.word_tokenize(text))[0][1]
if 'PRP' in pos:
    print(pos)