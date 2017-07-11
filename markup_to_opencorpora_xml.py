from pymorphy2 import MorphAnalyzer
import os


def head(text_params):
    head_lines = []
    head_lines.append('<? xml version=\"1.0\" encoding=\"utf-8\" ?>')
    head_lines.append('<text name=\"%s\" id=\"%d\" parent=\"%d\">' % (text_params['name'], text_params['id'], text_params['parent']))
    head_lines.append('<tags>')
    head_lines.append('  <tag>Год: %s</tag>' % text_params['year'])
    head_lines.append('  <tag>Дата: %s</tag>' % text_params['date'])
    head_lines.append('  <tag>Автор: %s</tag>' % text_params['author'])
    if isinstance(text_params['topic'], list):
        topics = ['  <tag>Тема: %s</tag>' % item for item in text_params['topic']]
        head_lines.append('\n'.join(topics))
    else:
        head_lines.append('  <tag>Тема: %s</tag>' % text_params['topic'])
    head_lines.append('</tags>\n')
    return '\n'.join(head_lines)


def main_xml(text):
    lines = []
    # blank line (\n\n) separates two paragraphs
    paragraphs = text.split('\n\n')
    for paragraph in paragraphs[1:]:
        sentence = []
        tokens_xml = []
        # each line — new analysis
        tokens = paragraph.split('\n')
        for token in tokens:
            # features are separated by \t
            features = token.split('\t')
            # 2nd feature: Text=wordform
            sentence.append(features[1].split('=')[1])
        lines.append('<source>' + ' '. join(sentence) + '</source>')
    return lines



def main():
    text_params = {
        'name': 'document_name',
        'id': 0,
        'parent': 0,
        'year': '0000',
        'date': '00/00',
        'author': 'some author',
        'topic': 'item1'
    }
    # head_document = head(text_params)
    with open('..' + os.sep + '140490813-#dev_conll_1_morph.csv', 'r', encoding='utf-8') as f:
        lines = f.read()
    paragraph = main_xml(lines)
    for line in paragraph:
        print(line)


if __name__ == '__main__':
    main()