import os
from pymorphy2 import tokenizers
from statistics import mean


""" Считает некоторые величины для корпуса, такие как:
- среднее кол-во слов в абзаце
- количество абзацев в тексте
- среднее количество абзацев на один текст
"""


def general_data():
    path_opencorpora = "." + os.sep + "!data" + os.sep + \
                       "newcorpus" + os.sep + "OpenCorpora_txt_clean"
    files = [item for item in os.listdir(path_opencorpora) if item.endswith(".txt")]
    total_pars = []
    total_avs = []
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


def parts_data():
    path_opencorpora = "." + os.sep + "!data" + os.sep + \
                       "newcorpus" + os.sep + "OpenCorpora_txt_clean"
    files = [item for item in os.listdir(path_opencorpora) if item.endswith(".txt")]
    parts = {(2, 109): [], (110, 214): [], (215, 316): [], (317, 416): [], (417, 519): [], (520, 656): [] }
    for file in files:
        text_id = int(file[:-4])
        for part in parts:
            if (part[0] <= text_id) and (text_id <= part[1]):
                file_path = path_opencorpora + os.sep + file
                with open(file_path, "r", encoding="utf-8") as f:
                    pars = f.readlines()
                    if len(pars) != 0:
                        parts[part].append(len(pars))
    for ids in parts:
        av_pars = sum(parts[ids])/100
        total = sum(parts[ids])
        print("id {:3d}–{:3d}:\t\t{:4d} абзацев\t\tв среднем на текст {:.2f}".format(ids[0], ids[1], total, av_pars))


def main():
    general_data()
    parts_data()


if __name__ == "__main__":
    main()
