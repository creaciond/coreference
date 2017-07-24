import os


def semclass_and_id(analysis):
    sem_class = ''
    sc_id = 0
    characteristics = analysis.split('\t')
    for charact in characteristics:
        if 'SC=' in charact:
            sem_char = charact.split('=')[1].split('(')
            sem_class = sem_char[0]
            sc_id = sem_char[1].strip(')')
            return sem_class, sc_id


def write_semclass(class_path, sc, sc_id):
    if not os.path.exists(class_path):
        with open(class_path, 'w', encoding='utf-8') as file_classes:
            file_classes.write('{0}\t{1}'.format(sc_id, sc))
    else:
        with open(class_path, 'a', encoding='utf-8') as file_classes:
            file_classes.write('\n{0}\t{1}'.format(sc_id, sc))


def main():
    class_path = '.' + os.sep + 'NLC' + os.sep + 'semclasses.txt'
    total = len(os.listdir('.' + os.sep + 'NLC'))
    i = 1
    for item in os.listdir('.' + os.sep + 'NLC'):
        if item.endswith('.csv'):
            path = '.' + os.sep + 'NLC' + os.sep + item
            with open(path, 'r', encoding='utf-8') as file:
                analyses = [line.strip('\n') for line in file.readlines() if line.strip('\n') != '']
                for analysis in analyses:
                    try:
                        sc, sc_id = semclass_and_id(analysis)
                        write_semclass(class_path, sc, sc_id)
                    except:
                        pass
            print('{0:.2f}%, file name: {1}'.format(i/total*100, item))
            i += 1


if __name__ == '__main__':
    main()
