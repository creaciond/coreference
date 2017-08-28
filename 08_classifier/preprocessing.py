import os
from sklearn.model_selection import train_test_split


def embeddings():
    embeddings_path = '.' + os.sep + 'embeddings.txt'
    embeddings_dict = {}
    for line in open(embeddings_path, 'r', encoding='utf-8').readlines()[1:]:
        items = line.strip('\r\n').split(maxsplit=1)
        # [:4] — берём только первые 4 значения из эмбеддингов
        embeddings_dict[items[0]] = [float(num) for num in items[1].split(' ')[:4]]
    # печатаем первые 4 семантических классоа, чтобы понять, всё ли верно
    # for semantic_class in list(embeddings_dict.keys())[:4]:
    #     print('semantic class: {0}, embeddings: {1}'.format(semantic_class, embeddings_dict[semantic_class]))
    return embeddings_dict


def syntpar():
    # работа с файлом
    syntax_paradigms_path = '.' + os.sep + 'ids2names' + os.sep + 'syntax_paradigms.txt'
    with open(syntax_paradigms_path, 'r', encoding='utf-8') as f_synt_par:
        # if '-1' not in line = если такая парадигма вообще есть в русском
        paradigms_info = [line.strip('\r\n') for line in f_synt_par.readlines() if '-1' not in line]
    # превращаем в словарь: ключ — id синт.парадигмы из разборов, значение — её название
    paradigms = {}
    for par_line in paradigms_info:
        par_parts = par_line.split('\t')
        par_name = par_parts[2]
        # если начинается с Synt, то надо убрать — в датасете это не так
        if par_name.startswith('Synt'):
            paradigms[par_parts[1]] = par_name[4:]
        else:
            paradigms[par_parts[1]] = par_name
    # заменяем все значения на бинаризованные массивы
    # ключ — id синт.парадигмы, значение — бинаризованный массив
    bin_paradigms = {}
    ids = list(paradigms.keys())
    for i in range(len(paradigms)):
        current_id = ids[i]
        binarized_synt = [float(0)] * len(ids)
        binarized_synt[i] = float(1)
        bin_paradigms[current_id] = binarized_synt
    # проверка: распечатываем все значения в виде массивов и их id
    # for each_id in ids:
    #     print('id: {0:>7}, name: {1:>17}, paradigm array: {2}'.format(each_id, paradigms[each_id],
    #                                                                   bin_paradigms[each_id]))
    return paradigms, bin_paradigms


def modify_token(token, embeddings_dict, synt_paradigms_bin):
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
            candidates_features.append(';'.join(token_parts[:-3]))
            group = token_parts[-3]
            if group != '-':
                candidates_results.append('1')
            else:
                candidates_results.append('0')
    # print('features: {0}, results: {1}'.format(len(candidates_features), len(candidates_results)))
    return candidates_features, candidates_results


def save_as_dataset(information, path, selection, values):
    path = path + '_' + values + '_' + selection + '.csv'
    new_information = []
    for piece in information:
        if (type(piece) != int) and (values != 'results'):
            line = ', '.join(piece)
            line = line.replace(']', '')
            line = line.replace('[', '')
            new_information.append(line)
        elif values == 'results':
            new_information.append(str(piece))
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_information))


def main():
    # данные для замены
    emb_dict = embeddings()
    par, bin_par = syntpar()
    # в этот список будет собираться вся инфа по токенам
    mention_candidates = []
    mention_candidates_results = []
    folder = '.' + os.sep + 'data_raw'
    for item in os.listdir(folder):
        if item.endswith('.csv'):
            # чтение из файла
            text_tokens = folder + os.sep + item
            print('working with file: {}'.format(text_tokens))
            with open(text_tokens, 'r', encoding='utf-8') as f:
                tokens = [line.strip('\n') for line in f.readlines()[1:]]
            print('overall, {} tokens'.format(len(tokens)))
            tokens = [modify_token(token, embeddings_dict=emb_dict, synt_paradigms_bin=bin_par) for token in tokens]
            # создаём внутри документа пары токенов
            pair_features, pair_results = create_pairs(tokens)
            # для отбора токенов на кандидаты в меншены
            synt_noun_id = '7'
            synt_noun_bin = str(bin_par[synt_noun_id])
            mention_candidates, mention_candidates_results = extract_mention_candidates(tokens, synt_noun_bin,
                mention_candidates, mention_candidates_results)
            #
            # сохранение
            ready_path = folder.replace('raw', 'ready')
            if not os.path.exists(ready_path):
                os.makedirs(ready_path)
            pairs_train, pairs_test, pairs_res_train, pairs_res_test = train_test_split(pair_features,
                pair_results, test_size=0.33)
            print('TRAIN: {0} features, {1} results'.format(len(pairs_train), len(pairs_res_train)))
            print('TEST: {0} features, {1} results'.format(len(pairs_test), len(pairs_res_test)))
            common_part = ready_path + os.sep + item[:-4]
            save_as_dataset(pairs_train, common_part, selection='train', values='features')
            save_as_dataset(pairs_test, common_part, selection='test', values='features')
            save_as_dataset(pairs_res_train, common_part, selection='train', values='results')
            save_as_dataset(pairs_res_test, common_part, selection='test', values='results')
        break


if __name__ == '__main__':
    main()