import os


def id_and_path(doc_ids_path):
    docs_info = {}
    with open(doc_ids_path, 'r', encoding='utf-8') as f_docs:
        info_docs = [info.strip('\n') for info in f_docs.readlines()[1:] if info.strip('\n') != '']
    for line in info_docs:
        items = line.split('\t')
        try:
            doc_id = items[0]
            path = items[1].replace('/', os.sep)
            docs_info[doc_id] = path
        except:
            print('error at line:\n{}'.format(line))
    return docs_info


def info_on_chains(table_path):
    entries_docs = {}
    with open(table_path, 'r', encoding='utf-8') as f_table:
        information = [info.strip('\n') for info in f_table.readlines()[1:] if info.strip('\n') != '']
        for info in information:
            items = info.split('\t')
            if items[0] not in entries_docs.keys():
                entries_docs[items[0]] = []
            entries_docs[items[0]].append('\t'.join(items[2:]))
    return entries_docs


def merge_dicts(doc_paths, entries_data):
    united_dict = {}
    for key in doc_paths:
        united_dict[key] = []
        united_dict[key].append(doc_paths[key])
        for entry in entries_data[key]:
            united_dict[key].append(entry)
    return united_dict

def main():
    # {'doc_id': 'path'}
    doc_ids_path = '..' + os.sep + 'RuCor' + os.sep + 'Documents.txt'
    doc_paths = id_and_path(doc_ids_path)
    # {'doc_id': [mention1, mention2, ...]}
    table_path = '..' + os.sep + 'RuCor' + os.sep + 'Groups.txt'
    entries_data = info_on_chains(table_path)
    # merge dicts:
    # {'doc_id': ['path', mention1, mention2, ...]}
    overall_dict = merge_dicts(doc_paths, entries_data)
    # parsed_textset_path = '..' + os.sep + 'RuCor' + os.sep + 'parsed_textset'


if __name__ == '__main__':
    main()
