import os
from lxml import etree


def parse_rdf(rdf_path):
    """
    Parses a given XML with information, extracts all the mentions and their offsets.

    Args:
        rdf_path (str): path to a file
    Returns:
        mentions (dict): dictionary with mentions and their IDs: [(start_offset, end_offset): "id"]
    """
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
            mentions[chain_id].append((mention_start, mention_end, mention_id))
    return mentions


def rdf_and_align(tokens, mentions):
    # токен из OpenCorpora — оффсет из OpenCorpora — оффсет токена от компрены
    new_tokens = []
    for token in tokens:
        offset = token[2]
        if offset in mentions:
            token.append(mentions[offset][0][0])
        new_tokens.append("\t".join(token))
    return new_tokens


def main():
    path_align = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "align"
    path_rdf = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "OpenCorpora_rdf"
    # new path
    path_mentions = ".." + os.sep + "!data" + os.sep + "newcorpus" + os.sep + "mentions"
    if not os.path.exists(path_mentions):
        os.mkdir(path_mentions)
    counter = 1
    total = len(os.listdir(path_align))
    for item in os.listdir(path_align):
        # get aligned tokens
        path_align_file = path_align + os.sep + item
        with open(path_align_file, "r", encoding="utf-8") as align_file:
            tokens = [line.strip("\n").split("\t") for line in align_file.readlines()]
        # work with RDF
        path_rdf_file = path_rdf + os.sep + item.replace("txt", "xml")
        if os.path.exists(path_rdf_file):
            mentions = parse_rdf(path_rdf_file)
            tokens = "\n".join(rdf_and_align(tokens, mentions))
        # save mentions
        mentions_file = path_mentions + os.sep + item
        with open(mentions_file, "w", encoding="utf-8") as mentions:
            mentions.write(tokens)
        print("{}/{} done".format(counter, total))
        counter += 1


if __name__ == "__main__":
    main()
