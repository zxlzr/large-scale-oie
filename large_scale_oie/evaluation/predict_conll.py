import sys
import os
sys.path.append(os.getcwd())
#learn more about python imports and relative paths
from allennlp.common.testing import AllenNlpTestCase
from allennlp.models.archival import load_archive
from allennlp.predictors import Predictor
from allennlp.data.tokenizers import WordTokenizer
from allennlp.data.tokenizers.word_splitter import SpacyWordSplitter
import json
from large_scale_oie.predictors.oie_predictor import OpenIePredictor
from large_scale_oie.models.oie_model import OieLabeler
import os
import numpy as np
import pandas as pd


def align_probs(instance_result, liabels):
    #method to align model output probabilities with the extracted tags
    probs = instance_result['class_probabilities']
    words = instance_result['words']
    tags = instance_result['tags']
    #demarcating the predicate index based on the index of the verb in the sentence. May need to
    #reconsider if the predicate form does not appear in the sentence
    pred_id = words.index(instance_result['verb'])
    #max_probs = np.amax(probs, axis = 1)
    #max_index = np.argmax(probs,axis=1)
    #max_label = map(lambda x: labels[x], max_index)
    tag_index = [labels.index(x) for x in tags]
    tag_probs = [probs[i,j] for i,j in enumerate(tag_index)]
    pred_ids = [pred_id]*len(tags)
    word_ids = list(range(len(tags)))
    df_dict = {'word_id': word_ids, 'words' :words ,'pred_id': pred_ids, 'tags': tags, 'probs':
               tag_probs}
    #df = pd.DataFrame.from_dict(df_dict)

    return df_dict



if __name__ == "__main__":

    labels = []
    #define the path to the model and define the conll file to write evaluation to
    #define path to sentences to run the model over
    sentence_file = 'oie-benchmark/raw_sentences/all.txt'
    sentence_output = 'oie-benchmark/raw_sentences/test_sent.jsonl'
    model_path = 'results/classic_fullrun/'
    output_path = 'large_scale_oie/evaluation/ex4.conll'
    #clear output file
    os.remove(output_path)

    with open(sentence_output, "w") as f:
        with open(sentence_file, "r") as sentences:
            for sentence in sentences:
                jsonl = '{' + '"' + 'sentence'  + '"'  + ' : ' + '"' +  sentence.replace('\n','') + '"' + '}'
                f.write(jsonl)
                f.write('\n')


    with open(model_path + 'vocabulary/labels.txt', "r") as vocab:
        for label in vocab:
            labels.append(label.rstrip())

    archive = load_archive('results/classic_fullrun/model.tar.gz')

    predictor = Predictor.from_archive(archive, 'oie')
    #iterate through sentences
    instance_iterator = 0
    #sentences = 'tests/fixtures/oie_test.jsonl'
    with open(sentence_output, "r") as sents:
        with open(output_path, 'a') as f:
            for sent in sents:
                 inp = json.loads(sent)
                 #run model on sentence
                 result = predictor.predict_json(inp)
                 for instance_result in result:
                     df = align_probs(instance_result, labels)
                     #write to conll file
                     lines =[str(wi)+'\t'+str(w)+'\t'+str(pi)+'\t'+str(t)+'\t'+str(p)\
                             for wi,w,pi,t,p in zip(df['word_id'],df['words'], df['pred_id'],
                                                    df['tags'], df['probs'])]
                     for line in lines:
                         f.write(line)
                         f.write('\n')
                     f.write('\n')

