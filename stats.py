import os
from pymorphy2 import tokenizers
from statistics import mean


def main():
    path_opencorpora = "." + os.sep + "!data" + os.sep + \
                       "newcorpus" + os.sep + "OpenCorpora_txt_clean"
    files = [item for item in os.listdir(path_opencorpora) if item.endswith(".txt")]
    total_avs = []
    total_pars = []
    total_pars_count = 0
    for file in files:
        with open(path_opencorpora + os.sep + file, "r", encoding="utf-8") as f:
            pars = f.readlines()
            total_pars_count += len(pars)
            total_pars.append(len(pars))
        try:
            av = []
            for par in pars:
                av.append(len(tokenizers.simple_word_tokenize(par)))
            total_avs.append(mean(av))
        except:
            # это пустые файлы
            pass
    print("В среднем слов в абзаце: {:.2f}\n".format(mean(total_avs)) +
          "Всего абзацев: {:,}\n".format(total_pars_count).replace(",", " ") +
          "В среднем абзацев в тексте: {:.2f}".format(mean(total_pars)))


if __name__ == "__main__":
    main()
