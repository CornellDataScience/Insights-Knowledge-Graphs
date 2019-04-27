#https://demo.allennlp.org/coreference-resolution/NzA1Mjk2

from allennlp.predictors.predictor import Predictor
predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz")

with open('raw_data.txt', encoding='UTF-8') as file:
  text = file.read()

open('coreference_output.txt', mode='w').close()
with open('coreference_output.txt', mode='a') as file:
    file.write(str(predictor.predict(text)))