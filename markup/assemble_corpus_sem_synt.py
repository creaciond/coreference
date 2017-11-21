import os
import re


def get_align(path):
    """
    Opens a file with alignment of tokens and turns it into a machine-readable
    dictionary.

    Args:
        path (str): path to file
    Returns:
        alignment (dict): dictionary containing alignment, where
            key = offset in Opencorpora (int)
            value = [token(str), offset in NLC(list of ints)]
    """
    alignment = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            token, oc_offset, nlc_offset = line.strip("\r\n").split("\t")
            oc_offset = int(oc_offset)
            nlc_offset = [int(offset) for offset in nlc_offset.split(", ")]
            alignment[oc_offset] = [token, nlc_offset]
    return alignment


def find_feature_value(feature, feature_list):
    """
    Finds a value of a given feature.

    Args:
        feature (str): feature we're interested in
        feature_list (list of strs): list of strs which may contain the feature

    Returns:
         value (str): value of the feature (if feature is present) or 'NA'
    """
    found = False
    i = 0
    while not found and i < len(feature_list):
        if feature in feature_list[i]:
            found = True
            value = feature_list[i].split('=')[1]
            if feature != "Text":
                value = re.sub("\D", "", value)
        else:
            i += 1
    if not found:
        value = "NA"
    return value


def parse_nlc(path):
    """
    Opens a file with NLC analyses and turns it into a machine-readable
    dictionary.

    Args:
        path (str): path to file.
    Returns:
        nlc_tokens (dict): dictionary containing semantic and syntactic
        information about tokens, where
            key = offset in NLC (int)
            value = [semantic_class(str), syntax_paradigm(str)]
    """
    nlc_tokens = {}
    with open(path, "r", encoding="utf-8") as nlc_file:
        raw_tokens = [line for line in nlc_file.readlines() if len(line) > 2]
    for raw_token in raw_tokens:
        items = raw_token.strip("\n").split("\t")
        offset = find_feature_value("Offset", items)
        offset = int(offset)
        semantic = find_feature_value("SC", items)
        syntax = find_feature_value("SP", items)
        nlc_tokens[offset] = [semantic, syntax]
    return nlc_tokens


def align_oc_nlc(alignments, nlc_info):
    """
    Inserts semantic and syntactic information, using OpenCorpora offsets.

    Args:
        alignments (dict): dictionary with alignment between OpenCorpora
            and NLC
        nlc_info (dict): dictionaty with information from NLC
    Returns:
        ready_list (list of strs): list with information to be saved
            - opencorpora offset
            - token
            - semantic class ID
            - syntax paradigm ID
    """
    ready_info = []
    for oc_offset in alignments:
        token, nlc_offsets = alignments[oc_offset]
        for nlc_offset in nlc_offsets:
            sem, synt = nlc_info[nlc_offset]
            info = "{}\t{}\t{}\t{}".format(oc_offset, token, sem, synt)
            ready_info.append(info)
    return ready_info


def save(info, path):
    """
    Saves annotation in a text file.

    Args:
        text (list of lists): tokens and their annotations
        path (str): path for a file
    Returns:
        none
    """
    with open(path, "w", encoding="utf-8") as f_save:
        f_save.write("\n".join(info))


def main():
    # align: book_2.txt, oc: book_2.tokens, nlc: books_2.csv
    path_align = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "align"
    path_nlc = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "nospaces_NLC"
    path_save = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "corpus_v3" + os.sep + "sem_synt"

    if not os.path.exists(path_save):
        os.mkdir(path_save)

    align_files = [file for file in os.listdir(path_align) if not file.startswith("!")]
    total = len(align_files)
    counter = 1

    for file_align in align_files:
        alignment = get_align(path_align + os.sep + file_align)
        nlc = parse_nlc(path_nlc + os.sep + file_align.replace("txt", "csv"))
        ready_info = align_oc_nlc(alignment, nlc)
        save(ready_info, path_save + os.sep + file_align)
        print("semantics/syntax done: {}/{}, {:2.2f}%, file: {}".format(counter, total,
                                                       counter / total * 100,
                                                       file_align))
        counter += 1


if __name__ == "__main__":
    main()