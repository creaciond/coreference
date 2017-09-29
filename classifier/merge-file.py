from datetime import datetime
from pymorphy2 import MorphAnalyzer
import os
import re


def read_info(file_path, header):
    """
    Reads information from file.

    Args:
        file_path (str) — path to file to be read
        header (bool) — whether there is any header in the file

    Returns:
        data (list of strs) — list of lines with information (all empty lines omitted)
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.readlines()
    if header:
        contents.remove(contents[0])
    data = [content.strip('\n') for content in contents if content.strip('\n') != '']
    return data


def find_feature_value(feature, feature_list):
    """
    Finds a value of a given feature.

    Args:
        feature (str) — feature we're interested in
        feature_list (list of strs) — list of strs which may contain the feature

    Returns:
         value (str) — value of the feature (if feature is present) or '0'
    """
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
    """
    Given a list of token annotations from ABBYY Compreno, transform it into dictionary.

    Args:
        annotations (list of strs) — list with annotations: each list item is
            a separate annotation

    Returns:
         NLC_dict (dict) — dict of annotations, keys are token offsets:
            {offset (str): annotations (dict)}
            annotations: {feature (str): value (str)}
    """
    NLC_dict = {}
    for annotation in annotations:
        annotation_parts = annotation.strip('\n').split('\t')
        annotation_dict = {}
        offset = find_feature_value('Offset=', annotation_parts)
        annotation_dict['wordform'] = find_feature_value('Text=', annotation_parts)
        annotation_dict['semantic_class'] = find_feature_value('SC=', annotation_parts)
        annotation_dict['semantic_slot'] = find_feature_value('SemSlot=', annotation_parts)
        annotation_dict['surface_slot'] = find_feature_value('SurfSlot=', annotation_parts)
        annotation_dict['syntax_paradigm'] = find_feature_value('SP=', annotation_parts)
        NLC_dict[offset] = annotation_dict
    return NLC_dict


def tokens_to_dict(annotations, doc_id):
    """
    Given a list of annotations from RuCor (token-wise), convert it to dictionary.

    Args:
        annotations (list of strs) — list with annotations: each list item is
            a separate annotation
        doc_id (str) — id of a given documents
    Returns:
        tokens_dict (dict) — dict of annotations, keys are token offsets:
            {offset (str): annotation_dict (dict)}
            annotation_dict: {feature (str): value (str)}
    """
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
    """
    Given a file with mapping of documents and their IDs, returns a dict with the mapping.

    Args:
        documents_path (str) — path to the file with informations
    Returns:
        names_doc_ids (dict) — dictionary with mapping of files and doc_ids:
            {filename (str): doc_id (str)}
    """
    info = read_info(documents_path, header=True)
    names_doc_ids = {}
    reg_name = re.compile('\/(.*?)\.txt')
    for line in info:
        parts = line.split('\t')
        doc_id = parts[0]
        filename = re.search(reg_name, parts[1]).group(1)
        names_doc_ids[filename] = doc_id
    return names_doc_ids


def merge_features(current_token, current_nlc):
    """
    Add information from NLC dictionary to annotation from RuCor dictionary.

    Args:
        current_token (dict) — annotation of a specific token from RuCor
        current_nlc (dict) — annotation of a specific token from NLC_dict
    Returns:
        current_token (dict) — updated RuCor annotation
    """
    current_token['wordform'] = current_nlc['wordform']
    current_token['semantic_class'] = current_nlc['semantic_class']
    current_token['semantic_slot'] = current_nlc['semantic_slot']
    current_token['surface_slot'] = current_nlc['surface_slot']
    current_token['syntax_paradigm'] = current_nlc['syntax_paradigm']
    return current_token


def text_and_tokens(rucor, nlc):
    """
    Updates annotation from RuCor with information extraced from NLC_dict.

    Args:
        rucor (dict) — all annotations from RuCor
        nlc (dict) — all annotations from NLC / ABBYY Compreno
    Returns:
         rucor (dict) — updated annontations with merged information
            from both dictionaries in args
    """
    nlc_offsets = set(nlc.keys())
    for item_offset in rucor:
        try:
            if item_offset in nlc_offsets:
                rucor[item_offset] = merge_features(rucor[item_offset], nlc[item_offset])
        except:
            print('error: {}'.format(item_offset))
    return rucor


def do_morphology(rucor, morph):
    """
    Adds morphological information for the token.
    Args:
        rucor (dict) — dictionary with token information
        morph (pymorphy2.MorphAnalyzer()) — morphological analyzer, used for morphological
            parsing of the token itself
    Returns:
        rucor (dict) — updated dictionary with morphological information
    """

    for token_offset in rucor:
        word = rucor[token_offset]['wordform']
        rucor[token_offset]['morphology'] = str(morph.parse(word)[0].tag)
    return rucor


def get_id(annot_string, regex):
    """
    Gives an ID of a particular value.

    Args:
        annot_string (str) — a string with a particular feature value and its ID in it
        regex (regular expression) — a regex for searching the ID
    Returns:
        id (str) — value ID
    """
    id = '0'
    try:
        id = re.search(string=annot_string, pattern=regex).group(1)
    except:
        pass
    return id


def line_to_write(annotation, reg_id):
    """
    Assembles a line to write in the dataset from a particular annotation.

    Args:
        annotation (dict) — annotation of a particular token
        reg_id (regular expression) — regex for searching value ID
    Returns:
        line (str) — line with token annotation
    """
    data = []

    if (annotation['morphology'] != 'PNCT') and ('semantic_class' in annotation):
        sem_class_id = get_id(annotation['semantic_class'], reg_id)
        sem_slot_id = get_id(annotation['semantic_slot'], reg_id)
        surf_slot_id = get_id(annotation['surface_slot'], reg_id)
        synt_par_id = get_id(annotation['syntax_paradigm'], reg_id)
        data = [sem_class_id, sem_slot_id, surf_slot_id, synt_par_id, annotation['morphology'],
                annotation['group_id'], annotation['chain_id'], annotation['link_id']]

    line = ','.join(data) + '\n'
    return line


def save_dataset(rucor, original_id):
    """
    Saves annotation as a dataset.

    Args:
        rucor (dict) — dictionary with annotations
        original_id (str) — ID of the original text
    Returns:
        none
    """

    folder_path = '..' + os.sep + '08_classifier' + os.sep + 'data_raw'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = folder_path + os.sep + original_id + '.csv'

    reg_id = re.compile('\(([0-9]+)\)')
    with open(file_path, 'w', encoding='utf-8') as dataset_file:
        for offset in rucor:
            line = line_to_write(rucor[offset], reg_id)
            if line != '\n':
                dataset_file.write(line)


def main():
    morph = MorphAnalyzer()
    reg_new_name = re.compile('[0-9]{,9}-#')

    tokens_path = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + '!new_tokens.txt'
    documents_path = tokens_path.replace('!new_tokens', 'Documents')
    nlc_folder = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + '!all-in-one'

    all_tokens = read_info(tokens_path, header=True)
    files_and_ids = filenames_ids(documents_path)
    filenames = set(files_and_ids.keys())

    counter = 1
    total = len(os.listdir(nlc_folder))

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
                save_dataset(rucor, original_id)
                # kinda logging print
                now = datetime.now()
                print('{0:2d}:{1:2d}:{2:2d}\t{3:3d}/{4:3d}\tfile: {5}\t\t\tdone: {6:.2f}%'.format(now.hour, now.minute,
                    now.second, counter, total, nlc_path, counter / total * 100))
                counter += 1


if __name__ == '__main__':
    main()
