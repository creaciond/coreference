from pymorphy2 import tokenizers
from pymorphy2 import MorphAnalyzer
import os


def morphology_features(tokens, morph):
    new_tokens = []
    for token in tokens:
        analysis = str(morph.parse(token)[0].tag)
        new_tokens.append(token + '\t' + analysis)
    return new_tokens


def write_info(tokens, path, fname):
    for i in range(len(tokens)):
        tokens[i] = str(i+1) + '\t' + tokens[i]
    path = path.replace('rucoref_texts', 'rucoref_new_parsed')
    if not os.path.exists(path):
        os.makedirs(path)
    fpath = path + os.sep + fname
    with open(fpath, 'w', encoding='utf-8') as new_file:
        new_file.write('\n'.join(tokens))


def main():
    morph = MorphAnalyzer()
    texts_path = '..' + os.sep + '..' + os.sep + 'RuCoref' + os.sep + 'rucoref_texts'
    for folder in os.listdir(texts_path):
        text_folder = texts_path + os.sep + folder
        for filename in os.listdir(text_folder):
            if filename.endswith('.txt'):
                with open(text_folder + os.sep + filename, 'r', encoding='utf-8') as source_file:
                    source_text = source_file.read()
                    # get tokens
                    tokens = tokenizers.simple_word_tokenize(source_text)
                    # parse tokens
                    tokens_with_tags = morphology_features(tokens, morph)
                    # write tokens to new file
                    write_info(tokens_with_tags, text_folder, filename)


if __name__ == '__main__':
    main()