import os
import re
from pymorphy2 import MorphAnalyzer


def open_texts_info():
    # ..\..\RuCor_original\Documents.txt — file with original paths and data
    path = '..' + os.sep + '..' + os.sep + 'RuCor_original' + os.sep + 'Documents.txt'
    # dictionary for storing information
    texts_info = {}
    with open(path, 'r', encoding='utf-8') as f_info:
        for line in f_info.readlines()[1:]:
            items = line.strip('\n').split('\t')
            # add folder separately
            file_name = items[1].split('/')[1]
            texts_info[file_name] = [items[1].split('/')[0]]
            has_URL = re.search('(?:https?://|www\.)(.*)?\t', line)
            if has_URL:
                texts_info[file_name].append(has_URL.group(0).strip('\t'))
            else:
                texts_info[file_name].append('')
    return texts_info


def clean_filename(file_name):
    reg_NLC = '[0-9]{,9}\-#(.*)?\.csv'
    '''
    returns a name with .txt extention, as in original RuCor:
    140773644-#2_astafiev_zhizn_prozhit.csv -> 2_astafiev_zhizn_prozhit.txt  
    '''
    true_name = str(re.search(reg_NLC, file_name).group(1)) + '.txt'
    return true_name


def head(text_params, file_name, text_count):
    txt_file_name = clean_filename(file_name)
    head_lines = ''
    if txt_file_name in text_params.keys():
        head_lines = head_lines + '\n' + '<? xml version=\"1.0\" encoding=\"utf-8\" ?>'
        head_lines = head_lines + '\n' + '<text name=\"%s\" id=\"%d\">' % (txt_file_name.strip('.txt'), text_count)
        text_count += 1
        head_lines = head_lines + '\n' + '<tags>'
        if text_params[txt_file_name][1] != '':
            head_lines = head_lines + '\n' + '<tag>url: %s</tag>' % text_params[txt_file_name][1]
        head_lines = head_lines + '\n' + '<tag>Тема: %s</tag>' % text_params[txt_file_name][0]
        head_lines = head_lines + '\n' + '</tags>\n'
    return head_lines, text_count


def original_paragraphs(path):
    with open(path, 'r', encoding='utf-8') as orig_file:
        or_paragraphs = []
        for line in re.split('\r?\n', orig_file.read()):
            line = line.strip('\t ')
            if line != '':
                or_paragraphs.append(line)
    return or_paragraphs


def set_borders(or_paragraphs, sem_sentences):
    paragraphs = []
    sentences = [sentence.split('\n') for sentence in sem_sentences]
    # sentences structure: [[str, str, str], [str, str], [str]]
    for or_paragraph in or_paragraphs:
        last_word = or_paragraph.split(' ')[-1].strip('.?!\":;»')
        last_pos = 0
        for sentence in sentences:
            if sentence != '':
                last_word_in_sentence = sentence[-1].split('\t')[1].split('=')[1]
                if last_word_in_sentence == last_word:
                    this_index = sentences.index(sentence)
                    paragraphs.append(sentences[last_pos:this_index])
    return paragraphs


def split_into_paragraphs(folder_path, file_name, text_params):
    # 0. initialization
    paragraphs = []
    # 1. open parsed file
    file_path = folder_path + os.sep + file_name
    with open(file_path, 'r', encoding='utf-8') as f_semantics:
        sem_sentences = f_semantics.read().split('\n\n')
    # 2.1. assemble path
    f_name = clean_filename(file_name)
    original_path = '..' + os.sep + '..' + os.sep + 'RuCor_original' + os.sep + 'rucoref_texts'
    original_file = original_path + os.sep + text_params[f_name][0] + os.sep + f_name
    # 2.2. retrieve normal paragraphs
    true_paragraphs = original_paragraphs(original_file)
    # 3. return paragraphs
    whatever = set_borders(true_paragraphs, sem_sentences)



def main():
    # initializing text counter and MorphAnalyzer
    text_count = 1
    morph = MorphAnalyzer()
    # text_params structure: 'filename': ['folder', 'url']
    text_params = open_texts_info()
    # semantics_path — path to files annotated automatically with semantics and syntax
    semantics_path = '..' + os.sep + '..' + os.sep + 'RuCor_semantics'
    for file in os.listdir(semantics_path):
        if file.endswith('.csv'):
            # 1. head and metainformation
            head_xml, text_count = head(text_params, file, text_count)
            # 2. divide into paragraphs
            paragraph_count = 1
            split_into_paragraphs(semantics_path, file, text_params)
            # 3. assemble sentences
            sentence_count = 1
            # 4. create tags for words
            word_count = 1
            # 5. final tags
            # 6. assemble
            # 7. save


if __name__ == '__main__':
    main()