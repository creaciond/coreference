import os


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
        value = '-1'
    return value


def sentence_to_dict(sentence_as_string):
    words_as_strings = sentence_as_string.split('\n')
    words_dict = {}
    ids_ar = []
    for word_as_string in words_as_strings:
        word_features = word_as_string.split('\t')
        offset = int(find_feature_value('Offset', word_features))
        words_dict[offset] = []
        parent_offset = int(find_feature_value('ParentOffset', word_features))
        words_dict[offset].append(parent_offset)
        words_dict[offset].append(find_feature_value('Text', word_features))
        words_dict[offset].append(find_feature_value('SP', word_features))
        # для дерева
        if parent_offset == -1:
            parent_offset = int(offset)
        ids_pair = (offset, parent_offset)
        ids_ar.append(ids_pair)
    return words_dict, ids_ar


def build_tree(nodelist):
    # pass 1: create nodes dictionary
    nodes = {}
    for item in nodelist:
        id, parent_id = item
        nodes[id] = {'id': id}
    # pass 2: create trees and parent-child relations
    forest = []
    for item in nodelist:
        id, parent_id = item
        node = nodes[id]
        # either make the node a new tree or link it to its parent
        if id == parent_id:
            # start a new tree in the forest
            forest.append(node)
        else:
            # add new_node as child to parent
            parent = nodes[parent_id]
            if not 'children' in parent:
                # ensure parent has a 'children' field
                parent['children'] = []
            children = parent['children']
            children.append(node)
    return forest[0]


def subtree(tree, NP_parts):
    this_id = tree['id']
    NP_parts.append(this_id)
    for dependent in tree['children']:
        if 'children' in dependent.keys():
            subtree(dependent, NP_parts)
        else:
            new_id = dependent['id']
            NP_parts.append(new_id)
    return NP_parts


def assemble_word(ids, words_dict):
    words = [words_dict[an_id][1] for an_id in ids]
    return ' '.join(words)


def extract_NPs(tree, words_dict):
    counter = 1
    for subtree_first in tree['children']:
        word_id = subtree_first['id']
        if 'Noun(7)' in words_dict[word_id][2]:
            NP_parts = []
            NP_parts = subtree(subtree_first, NP_parts)
            NP = assemble_word(sorted(NP_parts), words_dict)
            print('{0}) {1}'.format(counter, NP))
            counter += 1


def main():
    path_to_NLC = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + '!all-in-one'
    all_NPs = []
    for file in [file for file in os.listdir(path_to_NLC) if file.endswith('.csv')]:
        with open(path_to_NLC + os.sep + file, 'r', encoding='utf-8') as f:
            sentences = f.read().split('\n\n')
        for sentence in sentences:
            dict_sentence, ids = sentence_to_dict(sentence)
            tree = build_tree(ids)
            extract_NPs(tree, dict_sentence)
            break
        break



if __name__ == '__main__':
    main()