import os
import re


def get_mentions(file, folder, clear):
    mentions = set()
    reg_good_mentions = re.compile('type: good_mentions(.*?)(?:type)', flags=re.DOTALL)
    with open(folder + os.sep + file, 'r', encoding='utf-8') as f:
        if clear == True:
            mentions = set([line.strip('\n') for line in f.readlines() if line.strip('\n') != ''])
        else:
            for mentions_list in re.findall(reg_good_mentions, f.read()):
                actual_mentions = [mention for mention in mentions_list.split('\n') if mention != '']
                for each_mention in actual_mentions:
                    try:
                        true_mention = each_mention.split(': ')[1]
                        mentions.add(true_mention)
                    except:
                        print(each_mention)
        print('{0}: {1}'.format(file, len(mentions)))
    return mentions


def main():
    folder_path = '..' + os.sep + 'cort_vs_nps'
    for item in os.listdir(folder_path):
        if item.endswith('txt'):
            if 'nps' in item:
                mentions = get_mentions(item, folder_path, clear=True)
            else:
                mentions = get_mentions(item, folder_path, clear=False)


if __name__ == '__main__':
    main()