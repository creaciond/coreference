from pymorphy2 import MorphAnalyzer
import os


def split_into_tokens(text):
    tokens = []
    '''
        tokens
        -> sentence1: [token1:(features1), token2:(features2), ...]
    '''
    return tokens


def main():
    morph = MorphAnalyzer()
    texts_path = '..\\RuCoref\\rucoref_texts'
    for folder in os.listdir(texts_path):
        text_folder = texts_path + '\\' + folder
        for file in os.listdir(text_folder):
            if file.endswith('.txt'):
                file = text_folder + '\\' + file
                print(file)
                with open(file, 'r', encoding='utf-8') as source:
                    tokens = split_into_tokens(source.read())


if __name__ == '__main__':
    main()