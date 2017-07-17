import os
import re
from pymorphy2 import MorphAnalyzer
from pymorphy2 import tokenizers


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


def tokenize_and_morphology(or_paragraphs, morph):
    paragraphs_with_morpho = []
    for or_paragraph in or_paragraphs:
        tokens = tokenizers.simple_word_tokenize(or_paragraph)
        tokens_with_morpho = {}
        for token in tokens:
            analysis = str(morph.parse(token)[0].tag)
            tokens_with_morpho[token] = []
            tokens_with_morpho[token].append(analysis)
        paragraphs_with_morpho.append(tokens_with_morpho)
    # return
    return paragraphs_with_morpho


def split_into_paragraphs(file_name, text_params):
    # 1. assemble path
    f_name = clean_filename(file_name)
    original_path = '..' + os.sep + '..' + os.sep + 'RuCor_original' + os.sep + 'rucoref_texts'
    original_file = original_path + os.sep + text_params[f_name][0] + os.sep + f_name
    # 2. retrieve normal paragraphs
    true_paragraphs = original_paragraphs(original_file)
    # 3. tokenize paragraphs + add morphology
    morph = MorphAnalyzer()
    paragraphs_morpho = tokenize_and_morphology(true_paragraphs, morph)
    return paragraphs_morpho


def semantics_and_syntax(folder_path, file_name, paragraphs_morph):
    file_path = folder_path + os.sep + file_name
    with open(file_path, 'r', encoding='utf-8') as f_semantics:
        analyses = [line.strip('\n') for line in f_semantics.readlines()]
    for analysis in analyses:
        if analysis != '':
            items_analysis = analysis.split('\t')
            wordform = items_analysis[1].split('=')[1]
            for paragraph in paragraphs_morph:
                if wordform in paragraph.keys():
                    try:
                        # no ParentOffset = -1 characteristic
                        if 'ParentOffset' not in analysis:
                            lemma = str(items_analysis[2].split('=')[1])
                            surf_slot = str(items_analysis[5].split('=')[1])
                            sem_slot = str(items_analysis[6].split('=')[1])
                        else:
                            lemma = str(items_analysis[3].split('=')[1])
                            surf_slot = str(items_analysis[6].split('=')[1])
                            sem_slot = str(items_analysis[7].split('=')[1])
                        morpho = str(paragraph[wordform][0])
                        paragraph[wordform] = [lemma, morpho, sem_slot, surf_slot]
                    except:
                        buf = 1
    return paragraphs_morph


def do_xml(paragraphs):
    xml_ar = []
    sentence_count = 1
    word_count = 1
    xml_ar.append("<paragraphs>")
    for paragraph_count in range(len(paragraphs)):
        xml_ar.append('<paragraph id=\"%d\">' % (paragraph_count + 1))
        for sentence in paragraphs[paragraph_count]:
            # <sentence>
            xml_ar.append('<sentence id=\"%d\">' % sentence_count)
            # <source></source>
            source = ' '.join(paragraphs[paragraph_count].keys())
            xml_ar.append('<source>'+ source + '</source>')
            # <tokens>
            xml_ar.append('<tokens>')
            for key in paragraphs[paragraph_count].keys():
                # <token>
                xml_ar.append('<token text=\"%s\" id=\"%d\">' % (key, word_count))
                word_count += 1
                # <tfr>
                xml_ar.append('<tfr t=\"%s\" rev_id=\"@@@_@@"\>' % key)
                # <v>
                xml_ar.append('<v>')
                # <l>
                xml_ar.append('<l t=\"%s\" id=\"@@\">' % paragraphs[paragraph_count][key][0])
                # grammemes
                try:
                    tags = re.split('[ ,]', paragraphs[paragraph_count][key][1])
                    for tag in tags:
                        xml_ar.append('<g v=\"%s\" />' % tag)
                except:
                    buf = 1
                # semantics (if any)
                # syntax (if any)
                try:
                    xml_ar.append('<sc v=\"%s\" />' % paragraphs[paragraph_count][key][2])
                    xml_ar.append('<sc v=\"%s\" />' % paragraphs[paragraph_count][key][3])
                except:
                    buf = 1
                # </l>
                xml_ar.append('</l>')
                # </v>
                xml_ar.append('</v>')
                # </tfr>
                xml_ar.append('</tfr>')
                # </token>
                xml_ar.append('</token>')
            # </tokens>
            xml_ar.append('</tokens>')
            # </sentence>
            xml_ar.append('</sentence>')
            sentence_count += 1
        xml_ar.append('</paragraph>')
    xml_ar.append('</paragraphs>')
    xml_ar.append('</text>')
    return '\n'.join(xml_ar)


def save_new_file(folder, file_name, ready_xml):
    if not os.path.exists(folder):
        os.makedirs(folder)
    # save file
    with open(folder + os.sep + file_name, 'w', encoding='utf-8') as f_write:
        f_write.write(ready_xml)


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
            # 2. divide into paragraphs + add morphology
            paragraphs = split_into_paragraphs(file, text_params)
            paragraphs = semantics_and_syntax(semantics_path, file, paragraphs)
            # 3. create tags
            ready_xml = do_xml(paragraphs)
            # 4. assemble
            final_xml = head_xml + ready_xml
            # 5. save
            target_path = '..' + os.sep + '..' + os.sep + 'RuCor_new'
            filename = clean_filename(file)
            save_new_file(target_path, filename, final_xml)
            print(filename)


if __name__ == '__main__':
    main()