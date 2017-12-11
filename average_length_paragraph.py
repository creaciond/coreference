import os
from pymorphy2 import tokenizers
from statistics import mean


def main():
    path_opencorpora = "." + os.sep + "!data" + os.sep + \
                       "newcorpus" + os.sep + "OpenCorpora_txt_clean"
    files = [item for item in os.listdir(path_opencorpora) if item.endswith(".txt")]
    total_avs = []
    for file in files:
        with open(path_opencorpora + os.sep + file, "r", encoding="utf-8") as f:
            pars = f.readlines()
        try:
            av = []
            for par in pars:
                av.append(len(tokenizers.simple_word_tokenize(par)))
            total_avs.append(mean(av))
        except:
            # это пустые файлы
            pass
    print(mean(total_avs))



if __name__ == "__main__":
    main()
