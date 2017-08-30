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
            mention = group.split('\t')[7].strip(' \"')
            original_mentions.add(mention)
    extr_len = len(extracted_NPs)
    orig_len = len(original_mentions)
    print('Извлечённые NP: {0}, оригинальные меншены: {1}, итого: {2}'.format(extr_len, orig_len,
        extr_len + orig_len))
    print('Пересекающиеся меншены: {} шт.'.format(len(extracted_NPs & original_mentions)))
    difference = extracted_NPs ^ original_mentions
    print('Элементы, которые не в пересечении множеств: {} шт.'.format(len(difference)))
    for item in sorted(difference):
        print(item)


if __name__ == '__main__':
    main()