import re
from collections import Counter
import pandas as pd

import tqdm
from transformers import AutoTokenizer

from src.utils import load_json, dump_json, calculate_metrics, post_process, eliminar_repetidos, corregir_segmentacion, load_all_json_parts

class MorphologicalEvaluator:

    def __init__(self, tokenizers_paths:list):

        self.task1 = load_json('data/morph_quality.json')
        task2_directory = "data/task2"  
        self.task2 = load_all_json_parts(task2_directory)
        self.task3 = load_json('data/morph_segmentation.json')

        self.afixes = pd.read_csv('data/afixes.csv', usecols=['FORMA', 'TIPO', 'DERIVADOS'])
        self.prefixes = self.afixes[self.afixes['TIPO'].str.startswith('pref')]['FORMA'].values.tolist()
        self.suffixes = self.afixes[self.afixes['TIPO'].str.startswith('suf')]['FORMA'].values.tolist()

        self.tokenizers_paths = tokenizers_paths
               

    def eval_task1(self):

        """morphological relevance"""

        task_1_data = self.task1  
        
        task_1_results = {}

        for path in tqdm.tqdm(self.tokenizers_paths):  
            print(f"Evaluating {path}")
            results = {}
            tokenizer = AutoTokenizer.from_pretrained(path)
            vocab = tokenizer.get_vocab()
            vocab = list(vocab.keys())

            vocab = [post_process(word) for word in vocab]
            
            if 'bpe' in path or 'bne' in path:
                    vocab = ["##"+element if not element.startswith("Ġ") and not element.startswith("#") else element[1:] for i, element in enumerate(vocab)]

            elif 'unigram' in path:    
                vocab = ["##"+element if not element.startswith("▁") and not element.startswith("#") else element[1:] for i, element in enumerate(vocab)]

            for morph_type in task_1_data:
                
                print(f"Evaluating {morph_type}")
                words = task_1_data[morph_type]
                print(f"Total datos {morph_type}:", len(words))
                if type(words[0]) == type(words):
                    words = [word[0] for word in words]
                
                metrics = calculate_metrics(words, vocab)
                results[morph_type] = metrics

            task_1_results[path] = results
        
        dump_json(task_1_results, "results/task_1_results.json")


    def eval_task2(self):

        """morphological coherence"""

        all_words = self.task2

        task_2_results = {}

        task_2_results['prefixes'] = {}
        task_2_results['stems'] = {}
        task_2_results['suffixes'] = {}
        task_2_results['clitics'] = {}
        
        for path in tqdm.tqdm(self.tokenizers_paths):
            print(f"Evaluating {path}")
            tokenizer = AutoTokenizer.from_pretrained(path)

            results_dict = {}

            for i, morpheme_type in enumerate(all_words):

                print(f"Evaluating {morpheme_type}")
                words = all_words[morpheme_type]
                words = eliminar_repetidos(words)
                print(f"Total words {morpheme_type}:", len(words))

                monotoken = []
                multitoken_incorrect = []
                multitoken_correct = []

                morph_dict = {}
                morph_dict[morpheme_type] = {}

                for tuple in words:
                    
                    word = tuple[0]
                    morph = tuple[1]
                    
                    try:
                        tokens = tokenizer.tokenize(word)
                    except:
                        tokens = tokenizer.tokenize(tuple[0][0])

                    if 'unigram' in path:
                        tokens = ["##"+element if i>0 else element[1:] for i, element in enumerate(tokens)]
                    elif 'bpe' in path or 'bne' in path:
                        tokens = ["##"+element if i>0 else element for i, element in enumerate(tokens)]
                        tokens = corregir_segmentacion(tokens)

                    tokens = [post_process(word) for word in tokens]

                    if len(tokens) == 1:
                        monotoken.append([word, tokens])
                    else:
                        if morph in tokens:
                            multitoken_correct.append([word, tokens])
                        else: 
                            multitoken_incorrect.append([word, tokens])

                task_2_results[f"{morpheme_type}"][f"{path}_total"] =   len(words)
                task_2_results[f"{morpheme_type}"][f"{path}_monotoken"] =    f"{(len(monotoken)/len(words)) * 100:.2f}%"
                task_2_results[f"{morpheme_type}"][f"{path}_multitoken correct"] =   f"{(len(multitoken_correct)/len(words)) * 100:.2f}%"
                task_2_results[f"{morpheme_type}"][f"{path}_multitoken incorrect"] =   f"{(len(multitoken_incorrect)/len(words)) * 100:.2f}%"
                
                
        dump_json(task_2_results, 'results/task_2_results.json')


    def eval_tokenizer(self, path):

        "morphological accuracy"

        total = 0
        wrong = []
        correct = []
        m = 0

        l = 0

        tokenizer = AutoTokenizer.from_pretrained(path)

        t1 = []
        t2 = []
        t3 = []
        t4 = []

        vocab = tokenizer.get_vocab()
        vocab = list(vocab.keys())

        vocab = [post_process(word) for word in vocab]
        
        for word in self.task3:
            
            total += 1
            gold_segmentations = word[1]
            word = word[0]
            all_segmentations = []
            all_predictions = []

            for pos_tag in gold_segmentations:
                segmentation = gold_segmentations[pos_tag]
                all_segmentations.append(segmentation)

            all_predictions = tokenizer.tokenize(word)

            l += len(all_predictions)

            all_predictions = [re.sub('##', '', pred) for pred in all_predictions]
            all_predictions = [post_process(word) for word in all_predictions]
            all_predictions = [[re.sub('▁', '', pred) for pred in all_predictions]]

            intersection = [list(sublista) for sublista in map(tuple, all_predictions) if tuple(sublista) in map(tuple, all_segmentations)]

            if len(intersection) > 0:
                correct.append((word, all_predictions))
                if len(all_predictions[0]) == 1:
                    m += 1
            else:
                wrong.append((word, all_predictions))

                if len(all_predictions[0]) == 1 and len(all_segmentations[0]) > 1:
                    t1.append((word, all_predictions))
                elif len(all_predictions[0]) > 1 and len(all_segmentations[0]) == 1:
                    t2.append((word, all_predictions))
                else:
                    type3 = False
                    for segmentation in all_segmentations:
                        for i, token in enumerate(all_segmentations[0]):
                            
                            if 'bpe' in path or "unigram" in path:
                                token = re.sub('##', '', token)
                            if i == 0 and 'bpe' in path:
                                token = "Ġ"+token
                            if i == 0 and 'unigram' in path:
                                token = "▁"+token

                            if token not in vocab:
                                type3 = True
                                break
                            
                    if type3 == True:
                        t3.append((word, all_predictions))
                    else:
                        t4.append((word, all_predictions))

        
        errors = {
            1: len(t1),  
            2: len(t2),  
            3: len(t3),  
            4: len(t4), 
        }

        return len(correct)/total, errors  

    def eval_task3(self):

        results = {}
        all_errors = {}

        for path in self.tokenizers_paths:
            print(f"Evaluating {path}")
            score, errors = self.eval_tokenizer(path)  
            results[path] = score
            all_errors[path] = errors  
        
        dump_json(results, 'results/task_3_results.json')
        dump_json(errors, 'results/task_3_errors.json')


        return results, all_errors 


    def full_eval(self):

        self.eval_task1()
        self.eval_task2()
        self.eval_task3()