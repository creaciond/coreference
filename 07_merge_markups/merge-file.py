from datetime import datetime
from pymorphy2 import MorphAnalyzer
import os
import re

""" Opening and reading files """
def read_info(file_path, header):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.readlines()
    if header:
        contents.remove(contents[0])
    data = [content.strip('\n') for content in contents if content.strip('\n') != '']
    return data


def find_feature_value(feature, feature_list):
    found = False
    i = 0
    while not found and i < len(feature_list):
        if feature in feature_list[i]:
            found = True
            value = feature_list[i].split('=')[1]
        else:
            i += 1
    if not found:
        value = '0'
    return value


def NLC_to_dict(annotations):
    NLC_dict = {}
    for annotation in annotations:
        annotation_parts = annotation.strip('\n').split('\t')
        annotation_dict = {}
        offset = find_feature_value('Offset=', annotation_parts)
        annotation_dict['wordform'] = find_feature_value('Text=', annotation_parts)
        annotation_dict['syntax_surface'] = find_feature_value('SurfSlot=', annotation_parts)
        annotation_dict['synt_paradigm'] = find_feature_value('SP=', annotation_parts)
        annotation_dict['sem_surface'] = find_feature_value('SemSlot=', annotation_parts)
        annotation_dict['sem_deep'] = find_feature_value('SC=', annotation_parts)
        NLC_dict[offset] = annotation_dict
    return NLC_dict


def tokens_to_dict(annotations, doc_id):
    tokens_dict = {}
    for annotation in annotations:
        annotation_parts = annotation.strip('\n').split('\t')
        annotation_dict = {}
        if annotation.startswith(doc_id):
            offset = annotation_parts[1]
            annotation_dict['wordform'] = annotation_parts[3]
            annotation_dict['chain_id'] = annotation_parts[6]
            annotation_dict['group_id'] = annotation_parts[7]
            annotation_dict['link_id'] = annotation_parts[8]
            tokens_dict[offset] = annotation_dict
    return tokens_dict


def filenames_ids(documents_path):
    info = read_info(documents_path, header=True)
    names_doc_ids = {}
    reg_name = re.compile('\/(.*?)\.txt')
    for line in info:
        parts = line.split('\t')
        doc_id = parts[0]
        filename = re.search(reg_name, parts[1]).group(1)
        names_doc_ids[filename] = doc_id
    return names_doc_ids


""" Merging markups """
def merge_features(current_token, current_nlc):
    current_token['wordform'] = current_nlc['wordform']
    current_token['syntax_surface'] = current_nlc['syntax_surface']
    current_token['synt_paradigm'] = current_nlc['synt_paradigm']
    current_token['sem_surface'] = current_nlc['sem_surface']
    current_token['sem_deep'] = current_nlc['sem_deep']
    return current_token


def text_and_tokens(rucor, nlc):
    nlc_offsets = set(nlc.keys())
    for item_offset in rucor:
        try:
            if item_offset in nlc_offsets:
                rucor[item_offset] = merge_features(rucor[item_offset], nlc[item_offset])
        except:
            print('error: {}'.format(item_offset))
    return rucor


""" Morphology """
def do_morphology(rucor, morph):
    for token_offset in rucor:
        word = rucor[token_offset]['wordform']
        rucor[token_offset]['morphology'] = str(morph.parse(word)[0].tag)
    return rucor


""" Save as dataset """
def save_dataset(rucor):
    path = '..' + os.sep + '08_classifier' + os.sep + 'rucor_data.csv'
    with open(path, 'a', encoding='utf-8') as dataset_file:
        for offset in rucor:
            if (rucor[offset]['morphology'] != 'PNCT') and ('sem_deep' in rucor[offset]):
                data = [rucor[offset]['sem_deep'], rucor[offset]['sem_surface'], rucor[offset]['syntax_surface'],
                        rucor[offset]['synt_paradigm'], rucor[offset]['morphology']]
                if rucor[offset]['group_id'] != '-':
                    data.append('1')
                else:
                    data.append('0')
                dataset_file.write(';'.join(data) + '\n')


def main():
    """ Variables """
    morph = MorphAnalyzer()
    reg_new_name = re.compile('[0-9]{,9}-#')
    """ Various paths """
    tokens_path = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + '!new_tokens.txt'
    documents_path = tokens_path.replace('!new_tokens', 'Documents')
    nlc_folder = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + '!all-in-one'
    """ Some general data """
    all_tokens = read_info(tokens_path, header=True)
    files_and_ids = filenames_ids(documents_path)
    filenames = set(files_and_ids.keys())
    """ Percentage """
    counter = 1
    total = len(os.listdir(nlc_folder))
    """ Mapping: csv's — doc_id — tokens — NLC annotations """
    for item in os.listdir(nlc_folder):
        if item.endswith('.csv'):
            original_name = reg_new_name.sub('', item).strip('.csv')
            if original_name in filenames:
                # NLC
                nlc_path = nlc_folder + os.sep + item
                nlc = NLC_to_dict(read_info(nlc_path, header=False))
                # RuCor
                original_id = files_and_ids[original_name]
                rucor = tokens_to_dict(all_tokens, doc_id=original_id)
                # merging
                rucor = text_and_tokens(rucor, nlc)
                rucor = do_morphology(rucor, morph)
                # save
                save_dataset(rucor)
                # kinda logging print
                now = datetime.now()
                print('{0:2d}:{1:2d}:{2:2d}\t{3}/{4}, file: {5}, done: {6:.2f}%'. format(now.hour, now.minute, now.second,
                    counter, total, nlc_path, counter/total*100))
                counter += 1


if __name__ == '__main__':
    main()
