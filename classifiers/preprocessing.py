from datetime import datetime
from pymorphy2 import MorphAnalyzer
import re
import os
from sklearn.model_selection import train_test_split



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


def add_nlc_to_rucor(rucor, nlc):
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


def dataset(annotation):
    """
    Leaves information necessary only for dataset.

    Args:
        annotation (dict) — annotation of a particular token
    Returns:
        data (list of strs) — dataset information
    """
    data = []
    reg_id = re.compile('\(([0-9]+)\)')
    if (annotation['morphology'] != 'PNCT') and ('semantic_class' in annotation):
        sem_class_id = get_id(annotation['semantic_class'], reg_id)
        sem_slot_id = get_id(annotation['semantic_slot'], reg_id)
        surf_slot_id = get_id(annotation['surface_slot'], reg_id)
        synt_par_id = get_id(annotation['syntax_paradigm'], reg_id)
        data = [sem_class_id, sem_slot_id, surf_slot_id, synt_par_id, annotation['morphology'],
                annotation['group_id'], annotation['chain_id'], annotation['link_id']]
    return data


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


def embeddings():
    """
    Given a .txt file with embeddings of length 200, returns a dictionary containing the embeddings.

    Args:
        none
    Returns:
         embeddings_dict — dictionary, formatted as follows:
            {semantic_class_id (str): embeddings (list of floats)}
    """
    embeddings_path = '.' + os.sep + 'embeddings.txt'
    embeddings_dict = {}
    for line in open(embeddings_path, 'r', encoding='utf-8').readlines()[1:]:
        items = line.strip('\r\n').split(maxsplit=1)
        # [:4] — берём только первые 4 значения из эмбеддингов
        embeddings_dict[items[0]] = [float(num) for num in items[1].split(' ')[:4]]
    return embeddings_dict


def syntpar():
    """
    Given a path to the file containing all syntax paradigms and their IDs,
    returns the information as dictionaries.

    Args:
        none
    Returns:
        paradigms — map of syntax paradigm ID and its name:
            {id (str): name (str)}
        bin_paradigms — map of binarized syntax paradigms:
            {id (str): bin_paradigm (list of floats)}
    """
    # open file
    syntax_paradigms_path = '.' + os.sep + 'syntax_paradigms.txt'
    with open(syntax_paradigms_path, 'r', encoding='utf-8') as f_synt_par:
        # if '-1' in line = no such SyntParadigm in Russian
        paradigms_info = [line.strip('\r\n') for line in f_synt_par.readlines() if '-1' not in line]
    # paradgims — see in docstring above
    paradigms = {}
    for par_line in paradigms_info:
        par_parts = par_line.split('\t')
        par_name = par_parts[2]
        # SyntParadigm name edit: if starts with 'Synt', remove it
        if par_name.startswith('Synt'):
            paradigms[par_parts[1]] = par_name[4:]
        else:
            paradigms[par_parts[1]] = par_name
    # change SyntParadigm names into binarized lists
    bin_paradigms = {}
    ids = list(paradigms.keys())
    for i in range(len(paradigms)):
        current_id = ids[i]
        binarized_synt = [float(0)] * len(ids)
        binarized_synt[i] = float(1)
        bin_paradigms[current_id] = binarized_synt
    # check print
    ''' 
    for each_id in ids:
        print('id: {0:>7}, name: {1:>17}, paradigm array: {2}'.format(each_id, paradigms[each_id],
                                                                      bin_paradigms[each_id]))
    '''
    return paradigms, bin_paradigms


def modify_token(token, embeddings_dict, synt_paradigms_bin):
    """

    Args:
        token (str):
        embeddings_dict:
        synt_paradigms_bin:
    Returns:
    """
    token_items = token.split(';')
    sem_class = token_items[0]
    if sem_class in embeddings_dict.keys():
        sem_emb = str(embeddings_dict[sem_class])
    else:
        # если такого семантического класса нет в эмбеддингх, то просто нули
        sem_emb = str([0.0] * 4)
    token_items[0] = sem_emb
    synt_id = token_items[3]
    if synt_id in synt_paradigms_bin.keys():
        paradigm_bin = str(synt_paradigms_bin[synt_id])
    else:
        paradigm_bin = str([0] * len(synt_paradigms_bin))
    token_items[3] = paradigm_bin
    ready_token = ';'.join(token_items)
    return ready_token


def create_pairs(tokens):
    pairs = []
    pairs_result = []
    i = 0
    while i < len(tokens):
        token1 = tokens[i]
        chain_id_1 = token1.split(';')[-2]
        j = 0
        while j < len(tokens):
            if i != j:
                token2 = tokens[j]
                chain_id_2 = token2.split(';')[-2]
                if (chain_id_1 != '-') and (chain_id_2 != '-'):
                    token1_semantic = token1.split(';')[0]
                    token1_syntax = token1.split(';')[3]
                    token2_semantic = token2.split(';')[0]
                    token2_syntax = token2.split(';')[3]
                    pairs.append([token1_semantic, token1_syntax, token2_semantic, token2_syntax])
                    if (chain_id_1 in chain_id_2) or (chain_id_2 in chain_id_1):
                        pairs_result.append(1)
                    else:
                        pairs_result.append(0)
            j += 1
        i += 1
    # print('pairs: {0}, results: {1}'.format(len(pairs), len(pairs_result)))
    return pairs, pairs_result


def extract_mention_candidates(tokens, noun_paradigm, candidates_features, candidates_results):
    for token in tokens:
        token_parts = token.split(';')
        paradigm = token_parts[3]
        if paradigm == noun_paradigm:
            candidates_features.append(';'.join(token_parts[:-4]))
            group = token_parts[-3]
            if group != '-':
                candidates_results.append('1')
            else:
                candidates_results.append('0')
    # print('features: {0}, results: {1}'.format(len(candidates_features), len(candidates_results)))
    return candidates_features, candidates_results


def save_into_file(information, path, selection, values):
    path = path + '_' + selection + '_' + values + '.txt'
    new_information = []
    for piece in information:
        if values != 'results':
            if type(piece) == list:
                line = ', '.join(piece)
            else:
                line = piece
            line = line.replace(']', '')
            line = line.replace('[', '')
            line = line.replace(';', ', ')
            new_information.append(line)
        elif values == 'results':
            new_information.append(str(piece))
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_information))


def split_data(features, results):
    features_train, features_test, res_train, res_test = train_test_split(features,
        results, test_size=0.33)
    print('TRAIN: {0} features, {1} results'.format(len(features_train), len(res_train)))
    print('TEST: {0} features, {1} results'.format(len(features_test), len(res_test)))
    return features_train, features_test, res_train, res_test


def save_data(ready_path, features, results, filename):
    if not os.path.exists(ready_path):
        os.makedirs(ready_path)
    train, test, res_train, res_test = train_test_split(features, results, test_size=0.33)
    print('Train: {0} features, {1} results'.format(len(train), len(res_train)))
    print('Test: {0} features, {1} results'.format(len(test), len(res_test)))
    common_part = ready_path + os.sep + filename[:-4]
    save_into_file(train, common_part, selection='train', values='features')
    save_into_file(test, common_part, selection='test', values='features')
    save_into_file(res_train, common_part, selection='train', values='results')
    save_into_file(res_test, common_part, selection='test', values='results')


def add_embeddings_save(emb_dict, bin_par, tokens, doc_id):
    mention_candidates = []
    mention_candidates_results = []

    tokens = [modify_token(token, embeddings_dict=emb_dict, synt_paradigms_bin=bin_par) for token in tokens]

    # пары токенов: кореферентны или нет
    pair_features, pair_results = create_pairs(tokens)
    ready_path_pairs = '.' + os.sep + 'data_ready1' + os.sep + 'pairs'
    print('=== PAIRS ===')
    save_data(ready_path_pairs, pair_features, pair_results, filename=doc_id)

    # является ли токен меншеном
    synt_noun_id = '7'
    synt_noun_bin = str(bin_par[synt_noun_id])
    mention_candidates, mention_candidates_results = extract_mention_candidates(tokens, synt_noun_bin,
                                                                                mention_candidates,
                                                                                mention_candidates_results)
    ready_path_mentions = ready_path_pairs.replace('pairs', 'mentions')
    print('=== MENTIONS ===')
    save_data(ready_path_mentions, mention_candidates, mention_candidates_results, filename=doc_id)


def merge_files():
    morph = MorphAnalyzer()
    reg_new_name = re.compile('[0-9]{,9}-#')

    tokens_path = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + '!new_tokens.txt'
    documents_path = tokens_path.replace('!new_tokens', 'Documents')
    nlc_folder = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + '!all-in-one'

    all_tokens = read_info(tokens_path, header=True)
    files_and_ids = filenames_ids(documents_path)
    filenames = set(files_and_ids.keys())

    emb_dict = embeddings()
    par, bin_par = syntpar()

    for item in os.listdir(nlc_folder):
        if item.endswith('.csv'):
            original_name = reg_new_name.sub('', item).strip('.csv')
            if original_name in filenames:
                nlc_path = nlc_folder + os.sep + item
                nlc = NLC_to_dict(read_info(nlc_path, header=False))

                original_id = files_and_ids[original_name]
                rucor = tokens_to_dict(all_tokens, doc_id=original_id)

                united_annotation = add_nlc_to_rucor(rucor, nlc)
                united_annotation = do_morphology(united_annotation, morph)

                data = [dataset(united_annotation[token]) for token in united_annotation]
                add_embeddings_save(emb_dict, bin_par, data, original_name)
        break


def main():
    emb_dict = embeddings()
    par, bin_par = syntpar()

    # в этот список будет собираться вся инфа по токенам
    mention_candidates = []
    mention_candidates_results = []

    folder = ''
    for item in os.listdir(folder):
        if item.endswith('.csv'):
            text_tokens = folder + os.sep + item
            print('Working with file: {}'.format(text_tokens))
            # чтение из файла
            with open(text_tokens, 'r', encoding='utf-8') as f:
                tokens = [line.strip('\n') for line in f.readlines()[1:]]
            print('Overall: {} tokens'.format(len(tokens)))
            tokens = [modify_token(token, embeddings_dict=emb_dict, synt_paradigms_bin=bin_par) for token in tokens]
            # пары токенов: кореферентны или нет
            pair_features, pair_results = create_pairs(tokens)
            ready_path_pairs = folder.replace('raw', 'ready') + os.sep + 'pairs'
            print('=== PAIRS ===')
            save_data(ready_path_pairs, pair_features, pair_results, filename=item)
            # является ли токен меншеном
            synt_noun_id = '7'
            synt_noun_bin = str(bin_par[synt_noun_id])
            mention_candidates, mention_candidates_results = extract_mention_candidates(tokens, synt_noun_bin,
                mention_candidates, mention_candidates_results)
            ready_path_mentions = ready_path_pairs.replace('pairs', 'mentions')
            print('=== MENTIONS ===')
            save_data(ready_path_mentions, mention_candidates, mention_candidates_results, filename=item)
        break


if __name__ == '__main__':
    merge_files()