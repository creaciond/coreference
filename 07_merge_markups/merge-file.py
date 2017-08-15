from pymorphy2 import MorphAnalyzer
import re


def read_info(file_path, header):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.readlines()
    if header:
        contents.remove(contents[0])
    data = [content.strip('\n') for content in contents if content.strip('\n') != '']
    # for item in data:
    #     print(item)
    return data


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
        value = ''
    return value


def info_to_list(annotations, type):
    ready_list = []
    for annotation in annotations:
        annotation_parts = annotation.strip('\n').split('\t')
        annotation_dict = {}
        if type == 'NLC':
            annotation_dict['wordform'] = find_feature_value('Text=', annotation_parts)
            annotation_dict['offset'] = find_feature_value('Offset=', annotation_parts)
            annotation_dict['syntax_surface'] = find_feature_value('SurfSlot=', annotation_parts)
            annotation_dict['synt_paradigm'] = find_feature_value('SP=', annotation_parts)
            annotation_dict['sem_surface'] = find_feature_value('SemSlot=', annotation_parts)
            annotation_dict['sem_deep'] = find_feature_value('SC=', annotation_parts)
        elif type == 'tokens':
            annotation_dict['wordform'] = annotation_parts[3]
            annotation_dict['offset'] = annotation_parts[1]
            annotation_dict['chain_id'] = annotation_parts[6]
            annotation_dict['group_id'] = annotation_parts[7]
            annotation_dict['link_id'] = annotation_parts[8]
        ready_list.append(annotation_dict)
    return ready_list


def clean_text(text, token_length):
    text = text[token_length:]
    text = text.strip(' ')
    text = text.strip('\r\n')
    return text


def merge_features(current_token, current_nlc):
    current_token['wordform'] = current_nlc['wordform']
    current_token['syntax_surface'] = current_nlc['syntax_surface']
    current_token['synt_paradigm'] = current_nlc['synt_paradigm']
    current_token['sem_surface'] = current_nlc['sem_surface']
    current_token['sem_deep'] = current_nlc['sem_deep']
    return current_token


def do_morphology(rucor_tokens, morph):
    for token in rucor_tokens:
        token['morphology'] = str(morph.parse(token['wordform'])[0].tag)
    return rucor_tokens


def text_and_tokens(text, rucor, nlc):
    reg_punct = re.compile(r'[^\w\s]')
    rucor_count = 0
    rucor_total = len(rucor)
    nlc_count = 0
    while rucor_count < rucor_total:
        token = rucor[rucor_count]
        if text.startswith(token['wordform']):
            text = clean_text(text, len(token['wordform']))
            if not re.search(reg_punct, token['wordform']):
                # если токен NLC начинается с токена RuCor — полное или частичное совпадение по словоформе
                if nlc[nlc_count]['wordform'].startswith(token['wordform']):
                    # для слов с дефисами типа "ток-шоу": пропускаем 2 следующих токена
                    # — это части единого токена в NLC
                    if '-' in nlc[nlc_count]['wordform']:
                        token['wordform'] = nlc[nlc_count]['wordform']
                        rucor_count += 2
                        token = merge_features(token, nlc[nlc_count])
                    # для слов, где "не" токенизировалось отдельно, напр., "немедийный":
                    # добавляем информацию из _следующего_ токена в NLC
                    elif (nlc[nlc_count]['wordform'] == 'не' and
                                  nlc[nlc_count + 1]['wordform'] == token['wordform'][2:]):
                        nlc_count += 1
                        token = merge_features(token, nlc[nlc_count])
                    # для слов, где пробел разорвал токен, напр., "так что": пропускаем следующий токен в RuCor
                    elif ' ' in nlc[nlc_count]['wordform']:
                        rucor_count += 1
                        token = merge_features(token, nlc[nlc_count])
                    # остальные (i.e. нормальные) случаи
                    else:
                        token = merge_features(token, nlc[nlc_count])
                    nlc_count += 1
        rucor_count += 1
    return rucor


def main():
    """
        Тексты для проверки:
        !new_tokens.txt — есть заголовок
        140773643-#2.csv — нет заголовка, предложения отбиты пустой строкой
        2.txt — нет заголовка, чисто текст, один абзац = одна строка
    """
    morph = MorphAnalyzer()
    rucor = info_to_list(read_info('!new_tokens.txt', header=True), type='tokens')
    nlc = info_to_list(read_info('140773643-#2.csv', header=False), type='NLC')
    with open('2.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    rucor = text_and_tokens(text, rucor, nlc)
    rucor = do_morphology(rucor, morph)
    for i in range(len(rucor)):
        print('{0}:\n\t\t{1}'.format(i, rucor[i]))


if __name__ == '__main__':
    main()
