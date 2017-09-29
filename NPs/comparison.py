import os


def main():
    extracted_path = '.' + os.sep + 'NPs.txt'
    original_path = '..' + os.sep + '..' + os.sep + 'RuCor' + os.sep + 'Groups.txt'
    with open(extracted_path, 'r', encoding='utf-8') as f_extracted:
        extracted_NPs = set([item.strip('\n') for item in f_extracted.readlines()])
    with open(original_path, 'r', encoding='utf-8') as f_original:
        original_mentions = set()
        groups = [line.strip('\n') for line in f_original.readlines()[1:]]
        for group in groups:
            mention_extr = group.split('\t')[7].strip(' \"')
            original_mentions.add(mention_extr)
    extr_len = len(extracted_NPs)
    orig_len = len(original_mentions)
    print('Извлечённые NP: {0}, оригинальные меншены: {1}, итого: {2}'.format(extr_len, orig_len,
        extr_len + orig_len))
    # точное совпадение
    exact = extracted_NPs & original_mentions
    print('Пересекающиеся меншены: {} шт.'.format(len(exact)))
    # неточное совпадение
    substrings = set()
    for mention_extr in extracted_NPs:
        for mention_orig in original_mentions:
            if (mention_extr in mention_orig) or (mention_orig in mention_extr) and (mention_orig not in exact):
                substrings.add(mention_extr)
    print('Частичное совпадение: {} шт.'.format(len(substrings)))
    difference = extracted_NPs ^ original_mentions


if __name__ == '__main__':
    main()