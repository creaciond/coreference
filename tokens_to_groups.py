import os


def data_to_dict(path):
    data_dict = {}
    with open(path, 'r', encoding='utf-8') as f_data:
        information = [info.strip('\n') for info in f_data.readlines()[1:] if info.strip('\n') != '']
    for info in information:
        items = info.split('\t', maxsplit=1)
        doc_id = items[0]
        data = items[1]
        if doc_id not in data_dict.keys():
            data_dict[doc_id] = []
        data_dict[doc_id].append(data)
    return data_dict


def initial_data():
    tokens_path = '..' + os.sep + 'RuCor' + os.sep + 'Tokens.txt'
    groups_path = '..' + os.sep + 'RuCor' + os.sep + 'Groups.txt'
    return data_to_dict(tokens_path), data_to_dict(groups_path)


def tokens_to_dict(tokens):
    tokens_dict = {}
    for token in tokens:
        token_parts = token.split('\t', maxsplit=1)
        offset = token_parts[0]
        token_info = token_parts[1]
        tokens_dict[offset] = token_info
    return tokens_dict


def add_group_to_tokens(group, tokens_dict, tokens_mentioned):
    # initial info
    group_items = group.split('\t')
    group_id = group_items[1]
    chain_id = group_items[2]
    link_id = group_items[3]
    if ',' in group_items[7]:
        # many tokens in a group
        tk_shifts = group_items[7].split(',')
    else:
        tk_shifts = []
        tk_shifts.append(group_items[7])
    for offset in tk_shifts:
        if offset in tokens_dict.keys():
            token_info = tokens_dict[offset].split('\t')
            # len(token_info) >= 7 — have to write new info next to old
            if len(token_info) >= 7:
                token_info[4] = token_info[4] + ',' + group_id
                token_info[5] = token_info[5] + ',' + chain_id
                token_info[6] = token_info[6] + ',' + chain_id
                tokens_dict[offset] = '\t'.join(token_info)
            else:
                tokens_dict[offset] = '{0}\t{1}\t{2}\t{3}'.format(tokens_dict[offset], group_id, chain_id, link_id)
            # remove from mentioned tokens
            if offset in tokens_mentioned:
                tokens_mentioned.remove(offset)
    return tokens_dict, tokens_mentioned


def save_tokens(tokens, doc_id, path):
    if os.path.exists(path):
        done_tokens_file = open(path, 'a', encoding='utf-8')
    else:
        # initializing with a header
        done_tokens_file = open(path, 'w', encoding='utf-8')
        done_tokens_file.write('doc_id\tshift\tlength\ttoken\tlemma\tgram\tgroup_id\tchain_id\tlink_id\n')
    # printing offsets in correct order
    offsets_as_ints = [int(offset) for offset in tokens.keys()]
    for offset in sorted(offsets_as_ints):
        line = '{0}\t{1}\t{2}\n'.format(doc_id, offset, tokens[str(offset)])
        done_tokens_file.write(line)


def main():
    # getting all the data
    tokens_dict, groups_dict = initial_data()
    path_for_done_tokens = '..' + os.sep + 'RuCor' + os.sep + 'new_tokens.txt'
    # vars for logging
    doc_counter = 1
    total_docs = len(tokens_dict.keys())
    for doc_id in tokens_dict.keys():
        # for particular document
        tokens_in_doc = tokens_dict[doc_id]
        groups = groups_dict[doc_id]
        # tokens in format: {'offset': 'token_features'}
        tokens = tokens_to_dict(tokens_in_doc)
        # those left in tokens_mentioned have nothing in Groups, have to be filled with dashes
        tokens_mentioned = set(tokens.keys())
        # work with Groups
        for group in groups:
            tokens, tokens_mentioned = add_group_to_tokens(group, tokens, tokens_mentioned)
        # filling with dashes
        for offset in tokens_mentioned:
            tokens[offset] = '{0}\t-\t-\t-'.format(tokens[offset])
        # saving everything
        save_tokens(tokens, doc_id, path_for_done_tokens)
        # logging
        percentage = doc_counter/total_docs*100
        print('{0:.2f}%, doc id: {1}'.format(percentage, doc_id))
        doc_counter += 1


if __name__ == '__main__':
    main()