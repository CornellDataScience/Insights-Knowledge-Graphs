#!/usr/bin/env bash
allennlp predict https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz ./formatted_data.txt --predictor=open-information-extraction > predictions.txt