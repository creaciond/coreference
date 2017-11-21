import os


def read_tokens_info(path):
    """
    Given a path to the file with OpenCorpora tokens, returns its data
    in a machine-readable format.

    Args:
        path (str): path to the file to be read
    Returns:
        norm_text (list of lists): data from the file, formatted as:
            [token_id (str), start (int), len (int), token (str)]
    """
    norm_text = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if len(line) > 2:
                items = line.strip("\r\n").split(" ")
                norm_text.append([items[0], int(items[1]), int(items[2]), items[3]])
            else:
                norm_text.append("")
    return norm_text


def parse_rdf(rdf_path):
    """
    Parses a given XML with information, extracts all the mentions
    and their offsets.

    Args:
        rdf_path (str): path to a file
    Returns:
        mentions (dict): dictionary with mentions and their IDs:
        [(start_offset, end_offset): "id"]
    """
    from lxml import etree

    mentions = {}
    tree = etree.parse(rdf_path)
    root = tree.getroot()
    # AuxAnnotations
    for aux_annotation in root[-1].getchildren():
        # Aux:InstanceAnnotations
        for instance_annotation in aux_annotation.getchildren():
            mention_id = instance_annotation.attrib.values()[0]
            for child in instance_annotation.getchildren():
                if "annotation_start" in child.tag:
                    mention_start = child.text
                if "annotation_end" in child.tag:
                    mention_end = child.text
                if "instance" in child.tag:
                    chain_id = child.attrib.values()[0]
            if chain_id not in mentions:
                mentions[chain_id] = []
            mentions[chain_id].append((int(mention_start), int(mention_end), mention_id))
    return mentions


def nice_ids(chains):
    """
    Turns long and unreadable chain and mention IDs from RDF files into short
    and readable ones :)

    Args:
        chains (dict): dict with information on chains and mentions
            {chain_id (str): [mentions (tuples)]}
    Additional:
        mention (tuple): mention data, includes:
            - mention_start (int),
            - mention_end (int),
            - mention_id (str)
    Returns:
        ready_chains (dict): same info as in chains, but with human-readable IDs
    """
    ready_chains = {}
    prefix_chain = "ch_"
    prefix_mention = "m_"
    count_ch = 0
    count_men = 0
    normal_mention_names = {}
    for chain in chains:
        nice_chain = prefix_chain + "{:06}".format(count_ch)
        count_ch += 1

        ready_chains[nice_chain] = []
        for mention in chains[chain]:
            if mention[2] not in normal_mention_names:
                normal_mention_names[mention[2]] = prefix_mention + "{:06}".format(count_men)
                count_men += 1
            new_mention = (mention[0], mention[1],
                           normal_mention_names[mention[2]])

            ready_chains[nice_chain].append(new_mention)

    return ready_chains


def align(chains, text):
    """
    Assigns mention and chain IDs to the tokens from text.

    Args:
        chains (dict): chain and mention data
            structure: see in nice_ids()
        text (list of lists): machine-readable tokens from text
            structure: see in  read_tokens_info()
    Returns:
         text (list of lists): updated list of tokens, with mention and
         chain IDs from chains
            inner list structure:
            [token_id (str), start (int), len (int), token (str),
            mention_id (str), chain_id (str)]
            - if no mentions and chains, they are set to "-"
    """
    for entity in chains:
        mentions = chains[entity]
        for mention in mentions:
            for item in text:
                if type(item) == list:
                    if item[1] >= mention[0] and item[1] + item[2] <= mention[1]:
                        if len(item) == 4:
                            item.append(entity)
                            item.append(mention[2])
                        else:
                            item[4] = item[4] + "," + entity
                            item[5] = item[5] + "," + mention[2]
    for item in text:
        if type(item) == list and len(item) == 4:
            item += ["-", "-"]
    return text


def add_morph(text):
    """
    Adds lemma and morphological annotation, using Opencorpora tags.

    Args:
        text (list of lists): tokens and their annotation
            structure: see align()
    Returns:
         text (list of lists): updated information on tokens
            inner list structure:
            [token_id (str), start (int), len (int), token (str), lemma (str),
            morphology (str), mention_id (str), chain_id (str)]
    """
    import pymorphy2

    morph = pymorphy2.MorphAnalyzer()
    for item in text:
        if type(item) == list:
            wordform = item[3]
            lemma = morph.parse(wordform)[0].normal_form
            morphology = morph.parse(wordform)[0].tag
            item.insert(4, lemma)
            item.insert(5, str(morphology))
    return text


def save(text, path):
    """
    Saves annotation in a text file.

    Args:
        text (list of lists): tokens and their annotations
        path (str): path for a file
    Returns:
        none
    """
    with open(path, "w", encoding="utf-8") as f:
        for item in text:
            if isinstance(item, list):
                item[1] = str(item[1])
                item[2] = str(item[2])
                line = "\t".join(item)
            else:
                line = ""
            f.write(line + "\n")


def main():
    path_opencorpora = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "OpenCorpora_tokens"
    path_rdf = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "OpenCorpora_rdf"
    path_save = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "corpus_v3" + os.sep + "morph"

    if not os.path.exists(path_save):
        os.mkdir(path_save)

    oc_files = [file for file in os.listdir(path_opencorpora) if file.endswith("tokens")]
    total = len(oc_files)
    counter = 1

    for file_opencorpora in oc_files:
        try:
            path_oc_file = path_opencorpora + os.sep + file_opencorpora
            text = read_tokens_info(path_oc_file)

            rdf_file = file_opencorpora[:-7] + "_from_open_corpora_2.xml"
            path_rdf_file = path_rdf + os.sep + rdf_file
            chains_raw = parse_rdf(path_rdf_file)
            chains = nice_ids(chains_raw)

            text = align(chains, text)
            text = add_morph(text)

            path_save_file = path_save + os.sep + file_opencorpora.replace("tokens", "txt")
            save(text, path_save_file)

            print("align and morphology done: {}/{}, {:2.2f}%, file: {}".format(counter, total, counter/total*100,
                file_opencorpora.replace("tokens", "txt")))
        except:
            pass
        counter += 1


if __name__ == "__main__":
    main()