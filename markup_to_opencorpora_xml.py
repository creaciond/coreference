from pymorphy2 import MorphAnalyzer
import os


def head(text_params):
    head_lines = []
    head_lines.append('<? xml version=\"1.0\" encoding=\"utf-8\" ?>')
    head_lines.append('<text name=\"%s\" id=\"%d\" parent=\"%d\">' % (text_params['name'], text_params['id'], text_params['parent']))
    head_lines.append('<tags>')
    head_lines.append('  <tag>Год: %s</tag>' % text_params['year'])
    head_lines.append('  <tag>Дата:  %s</tag>' % text_params['date'])
    head_lines.append('  <tag>Автор: %s</tag>' % text_params['author'])
    if isinstance(text_params['topic'], list):
        topics = ['  <tag>Тема: %s</tag>' % item for item in text_params['topic']]
        head_lines.append('\n'.join(topics))
    else:
        head_lines.append('  <tag>Тема: %s</tag>' % text_params['topic'])
    head_lines.append('</tags>\n')
    return '\n'.join(head_lines)


def main():
    text_params = {
        'name': 'name',
        'id': 0,
        'parent': 0,
        'year': '0000',
        'date': '00/00',
        'author': 'some author',
        'topic': ['item1', 'item1/morespecific1']
    }
    print(head(text_params))


if __name__ == '__main__':
    main()