import os
import re
import string
import time


def rename_nlc(path):
    """
    Renames files, removes NLC info (job number, etc).

    Args:
        path (str): path to folder
    Returns:
        none
    """
    reg_file_name = re.compile("[0-9]+?-#(book_[0-9]+?\.csv)")
    for file in os.listdir(path):
        if file.endswith('.csv') and re.search(reg_file_name, file):
            print(file)
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


def offsets_NLC(file):
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


def merge(NLC_tokens, NLC_offsets, OC_tokens, OC_offsets):
    """
    Merges two markups, of OpenCorpora and of ABBYY NLC, so that NLC tokens are aligned to OpenCorpora's (OC).

    Args:
        NLC_tokens (list): list of NLC tokens in the given text
        NLC_offsets (list): list of starting offsets for the correpsonding tokens
        OC_tokens (list): list of OC tokens extracted from the given text
        OC_offsets (list): list of starting offsets for the correpsonding tokens
    Returns:
        alignment (list of tuples): list where each tuple stands for token alignment, formatted as follows:
            (token in OC (str), offset in OC (int), token in NLC (str), offset in NLC (int))

    TODO:
    починить костыль с str() для случаев, когда 1 токену OC соответствует два в NLC
    """
    alignment = []
    for OC_offset in OC_offsets:
        ind_OC = OC_offsets.index(OC_offset)
        if (OC_offset in NLC_offsets) and (OC_tokens[ind_OC] not in string.punctuation):
            ind_NLC = NLC_offsets.index(OC_offset)
            NLC_tok = NLC_tokens[ind_NLC]
            NLC_off = NLC_offsets[ind_NLC]
            if (ind_NLC <= len(NLC_tokens)-2) and (ind_OC <= len(OC_tokens)-2):
                if NLC_offsets[ind_NLC + 1] < OC_offsets[ind_OC + 1]:
                    tok = [NLC_tokens[ind_NLC], NLC_tokens[ind_NLC+1]]
                    off = [str(NLC_offsets[ind_NLC]), str(NLC_offsets[ind_NLC+1])]
                    NLC_tok = ", ".join(tok)
                    NLC_off = ", ".join(off)
            tup = (OC_tokens[ind_OC], OC_offsets[ind_OC], NLC_tok, NLC_off)
            alignment.append(tup)
    # alignment = alignment.sort(key=lambda line: line[1])
    return alignment


def save_merged(alignment, path):
    """
    Saves the alignment
    Args:
        alignment (list of tuples): list where each tuple stands for token alignment, formatted as follows:
            (token in OC (str), offset in OC (int), token in NLC (str), offset in NLC (int))
        path (str): path to save at
    Returns:
        none
    """
    with open(path, "w", encoding="utf-8") as save_map:
        for piece in alignment:
            save_map.write("{}\t{}\t{}\n".format(piece[0], piece[1], piece[3]))


def main():
    path_NLC = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "nospaces_NLC"
    path_OC = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "newtokens_OC"
    path_align = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "align"
    if not os.path.exists(path_align):
        os.makedirs(path_align)
    # uncomment following if it's the first code run; otherwise does nothing
    # rename_nlc(path_NLC)
    NLC_files = [file for file in os.listdir(path_NLC) if file.endswith(".csv")]
    counter = 1
    total = len(NLC_files)
    begin = time.time()
    for NLC_file in NLC_files:
        # tokens from both files
        NLC_tokens, NLC_offsets = offsets_NLC(path_NLC + os.sep + NLC_file)
        OC_path = path_OC + os.sep + re.sub("csv", "tokens", NLC_file)
        OC_tokens, OC_offsets = offsets_opencorpora(OC_path)
        # merge and save
        align = merge(NLC_tokens, NLC_offsets, OC_tokens, OC_offsets)
        file_align = path_align + os.sep + re.sub("csv", "txt", NLC_file)
        save_merged(align, file_align)
        # logging print
        print("{}/{} files, name: {}, ready: {:.2f}%".format(counter, total, NLC_file, counter/total*100))
        counter += 1
    end = time.time()
    print("Started at {}, ended at {}, time consumed: {}".format(time.ctime(begin),
        time.ctime(end), end-begin))


if __name__ == "__main__":
    main()