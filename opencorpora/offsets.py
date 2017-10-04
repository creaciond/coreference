import os
import re
import string


def rename_nlc(path):
    """
    Renames files, removes NLC info (job number, etc).

    Args:
        path (str): path to folder
    Returns:
        none
    """
    reg_file_name = re.compile("[0-9]+?-#([0-9]+?\.csv)")
    for file in os.listdir(path):
        if file.endswith('.csv') and re.search(reg_file_name, file):
            filepath = path + os.sep + file
            norm_name = path + os.sep + re.search(reg_file_name, file).group(1)
            os.rename(filepath, norm_name)


def offsets_opencorpora(file):
    """
    Reads from a file with OpenCorpora tokenization.

    Args:
        file (str): path to file
    Returns:
        tokens (list): list of tokens
        offsets (list): list of starting offsets for the correpsonding tokens
    """
    with open(file, "r", encoding="utf-8") as f:
        text = f.readlines()
    tokens = []
    offsets = []
    for line in text:
        elems = line.strip("\n").split(" ")
        if len(elems) > 1:
            token = elems[3]
            token = re.sub("й", "й", token)
            tokens.append(token)
            offset_start = int(elems[1])
            offsets.append(offset_start)
    return tokens, offsets


def offsets_parsed(file):
    """
        Reads from a file with NLC tokenization and annotation.

        Args:
            file (str): path to file
        Returns:
            tokens (list): list of tokens
            offsets (list): list of starting offsets for the correpsonding tokens
        """
    with open(file, "r", encoding="utf-8") as f:
        lines = [line.strip("\r\n") for line in f.readlines() if line != '\r\n']
    tokens = []
    offsets = []
    for line in lines:
        annotations = line.split("\t")
        if len(annotations) > 1:
            token = re.sub("Text=", "", annotations[1])
            token = re.sub("й", "й", token)
            offset_start = int(re.sub("Offset=", "", annotations[0]))
            tokens.append(token)
            offsets.append(offset_start)
    return tokens, offsets


def try_merge_tokens(tokens_orig, offsets_orig, tokens_nlc, offsets_nlc):
    i = 0
    j = 0
    offsets_map = []
    while i <= min(len(offsets_orig, offsets_nlc)):
        if offsets_orig[i] == offsets_nlc[j]:
            if len(tokens_orig[i]) == len(tokens_nlc[j]):
                offsets_map.append((offsets_orig[i], offsets_orig[i]))
                i += 1
                j += 1
            if tokens_orig[i] in string.punctuation:
                offsets_map.append((offsets_orig[i], -1))
                i += 1
            if len(tokens_orig[i]) < len(tokens_nlc[j]):
                if tokens_orig[i] + tokens_orig[i+1] == tokens_nlc[j]:
                    offsets_map.append((offsets_orig[i], offsets_nlc[j]))
                    offsets_map.append((offsets_orig[i+1], offsets_nlc[j]))
                    i += 2
                    j += 1
            if len(tokens_orig[i]) > len(tokens_nlc[j]):
                if tokens_nlc[j] + tokens_nlc[j+1] == tokens_orig[i]:
                    nlc_list = [offsets_nlc[j], offsets_nlc[j+1]]
                    offsets_map.append((offsets_orig[i], nlc_list))
                    i += 1
                    j += 2


def difference(first, second):
    return [item for item in first if item not in second]


def easy_merge(tokens_orig, offsets_orig, tokens_nlc, offsets_nlc):
    mapping = []
    # i = 0
    # j = 0
    # while (i <= len(tokens_orig)):
    #     if tokens_orig[i] == tokens_nlc[j]:
    #         mapping.append((tokens_orig[i], offsets_orig[i], tokens_nlc[j], offsets_nlc[j]))
    #         j += 1
    #     else:
    #         in1 = " ".join([tokens_orig[i], tokens_orig[i+1], tokens_orig[i+2]])
    #         if in1 == tokens_nlc[j]:
    #             mapping.append((tokens_orig[i], offsets_orig[i], tokens_nlc[j], offsets_nlc[j]))
    #             i += 2
    #             j += 1
    #         else:
    #             print(tokens_orig[i], "vs", tokens_nlc[j])
    #     i += 1
    for token in tokens_orig:
        if token in tokens_nlc:
            info = (token, offsets_orig[tokens_orig.index(token)], token, offsets_nlc[tokens_nlc.index(token)])
            print(info)
            mapping.append(info)
    return mapping



def main():
    newcorpus_path = ".." + os.sep + "!data" + os.sep + "newcorpus"
    path_original = newcorpus_path + os.sep + "oldtokens"
    path_parsed = newcorpus_path + os.sep + "nospaces_nlc"
    path_opencorpora = newcorpus_path + os.sep + "newtokens"

    for item in os.listdir(path_original):
        doc_id = item[:-4]
        print(doc_id)
        doc_parsed = path_parsed + os.sep + doc_id + ".csv"
        doc_opencorpora = path_opencorpora + os.sep + "book_" + doc_id + ".tokens"

        opencorpora_tokens, opencorpora_offsets = offsets_opencorpora(doc_opencorpora)
        nlc_tokens, nlc_offsets = offsets_parsed(doc_parsed)
        print("OpenCorpora: {} tokens, NLC: {} tokens".format(len(opencorpora_tokens), len(nlc_tokens)))

        map = easy_merge(opencorpora_tokens, opencorpora_offsets, nlc_tokens, nlc_offsets)

        break


if __name__ == "__main__":
    main()