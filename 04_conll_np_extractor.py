import os
import re


def get_sentences(conll_file):
    sentences = open(conll_file, 'r', encoding='utf-8').read().split('\n\n')
    clean_sentences = []
    for sentence in sentences:
        lines = sentence.split('\n')
        for line in lines:
            if line.startswith('#'):
                lines.remove(line)
        if lines != []:
            clean_sentences.append(lines)
    return clean_sentences


def assemble_tree(sentence):
    sentence_tags = ''
    punct = set('.,?!-\"')
    for line in sentence:
        items = line.strip('\n').split('\t')
        try:
            if '*' in items[5]:
                if items[4] not in punct:
                    substitution = ' ' + items[4] + '=\"' + items[3] + '\"'
                else:
                    substitution = ' PUNCT=\"' + items[3] + '\"'
                items[5] = items[5].replace('*', substitution)
            sentence_tags += items[5]
        except:
            pass
    '''
        uncomment following line for printing a syntax tree at 
        http://mshang.ca/syntree/
    '''
    # sentence_tags = sentence_tags.replace('(', '[').replace(')', ']')
    return sentence_tags


def clean_NPs(NPs_raw, NP_set):
    reg_word = '\"(.+?)\"'
    for np in NPs_raw:
        clean_np = ' '.join(re.findall(reg_word, np))
        NP_set.add(clean_np)
    return NP_set


def retrieve_NPs(sentence, NPs):
    reg_NP = 'NP (?:[A-Z]+?=\".*?\" ?)+?\)'
    NPs_raw = re.findall(reg_NP, sentence)
    NPs = clean_NPs(NPs_raw, NPs)
    return NPs


def save_NPs(NPs, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(NPs)))


# i'm really, really sorry
def main():
    # initializing
    conll_path = '..' + os.sep + 'conll_compreno.txt'
    sentences = get_sentences(conll_path)
    trees = []
    NPs = set()
    # markup -> trees
    for sentence in sentences:
        trees.append(assemble_tree(sentence))
    for tree in trees:
        NPs = retrieve_NPs(tree, NPs)
    save_path = conll_path.replace('compreno', 'nps')
    save_NPs(NPs, save_path)


if __name__ == '__main__':
    main()