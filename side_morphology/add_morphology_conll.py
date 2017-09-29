from pymorphy2 import MorphAnalyzer
import os


def do_morph(tokens, morph_analyzer):
    new_tokens = []
    '''
    first 5 lines — document description (no morphology required),
    6th line — empty
    '''
    for i in range(len(tokens)):
        if i <= 5:
            new_tokens.append(tokens[i].strip('\r\n'))
        else:
            # if line length is 2, it's empty
            if len(tokens[i]) > 2:
                # word retrieval
                elements = tokens[i].split('\t')
                token = elements[1].split('=')[1]
                analysis = str(morph_analyzer.parse(token)[0].tag)
                # line assemble
                new_tokens.append(tokens[i].strip('\r\n') + '\t' + 'MORPH=' + analysis)
    return new_tokens


def main():
    morph = MorphAnalyzer()
    # open
    filename = '..' + os.sep + '140490813-#dev_conll_1.csv'
    with open(filename, 'r', encoding='utf-8') as file_markup:
        tokens = file_markup.readlines()
    # do morphology
    tokens_morph = do_morph(tokens, morph)
    # new file path
    new_file = filename.replace('.csv','_morph.csv')
    # write to new file
    with open(new_file, 'w', encoding='utf-8') as file_with_morph:
        file_with_morph.write('\n'.join(tokens_morph))


if __name__ == '__main__':
    main()