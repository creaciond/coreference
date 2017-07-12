import os
import re
from pymorphy2 import MorphAnalyzer


def head(text_params):
    head_lines = []
    head_lines.append('<? xml version=\"1.0\" encoding=\"utf-8\" ?>')
    head_lines.append('<text name=\"%s\" id=\"%d\" parent=\"%d\">' % (text_params['name'], text_params['id'], text_params['parent']))
    head_lines.append('<tags>')
    head_lines.append('<tag>Год: %s</tag>' % text_params['year'])
    head_lines.append('<tag>Дата: %s</tag>' % text_params['date'])
    head_lines.append('<tag>Автор: %s</tag>' % text_params['author'])
    if isinstance(text_params['topic'], list):
        topics = ['<tag>Тема: %s</tag>' % item for item in text_params['topic']]
        head_lines.append('\n'.join(topics))
    else:
        head_lines.append('<tag>Тема: %s</tag>' % text_params['topic'])
    head_lines.append('</tags>\n')
    return '\n'.join(head_lines)


def break_into_sentences(folder_path):
    sentences = []
    for file in os.listdir(folder_path):
        if file.endswith('csv'):
            file_path = folder_path + os.sep + file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.read()
                raw_sentences = lines.split('\n\n')
                for raw_sentence in raw_sentences:
                    analyses = raw_sentence.split('\n')
                    sentences.append(analyses)
                # work on one text for now
                break
    return sentences


def source_from_sentence(sentence):
    words = []
    for analysis in sentence:
        if analysis != '':
            items = analysis.split('\t')
            word_form = items[1].split('=')[1]
            if word_form != '':
                words.append(word_form)
    source = '<source>' + ' '.join(words) + '</source>'
    return source


def grammar_tags(sentence, word_count, morph):
    lines_tags = []
    lines_tags.append('<tokens>')
    for analysis in sentence:
        if analysis != '':
            items = analysis.split('\t')
            word = items[1].split('=')[1]
            lemma = items[3].split('=')[1]
            try:
                semantic_class = items[7].split('=')[1]
                surface_slot = items[6].split('=')[1]
            except:
                semantic_class = items[6].split('=')[1]
                surface_slot = items[5].split('=')[1]
            lines_tags.append('<token text=\"%s\" id=\"%d\">' % (word, word_count))
            word_count += 1
            lines_tags.append('<tfr t=\"%s\" rev_id=\"@@@_@@\">' % word)
            lines_tags.append('<v>')
            lines_tags.append('<l t=\"%s\" id=\"@@\">' % lemma)
            # add morphology
            morph_analysis = str(morph.parse(word)[0].tag)
            tags = re.split('[ ,]', morph_analysis)
            for tag in tags:
                lines_tags.append('<g v=\"%s\" />' % tag)
            # add semantics
            lines_tags.append('<sc v=\"%s\" />' % semantic_class)
            # add syntax
            lines_tags.append('<ss v=\"%s\" />' % surface_slot)
            # closing tags
            lines_tags.append('</l>')
            lines_tags.append('</v>')
            lines_tags.append('</tfr>')
            lines_tags.append('</token>')
    lines_tags.append('</tokens>')
    return '\n'.join(lines_tags)


def main():
    # all XML will be stored here
    lines_xml = ''
    # the following are dummy parameters, just for check
    text_params = {
        'name': 'document_name',
        'id': 0,
        'parent': 0,
        'year': '0000',
        'date': '00/00',
        'author': 'some author',
        'topic': ['item1', 'item1/sub-item1']
    }
    # todo: fix metainfo
    # head in XML format
    lines_xml = head(text_params)
    # counters for items
    paragraph_count = 1
    sentence_count = 1
    word_count = 1
    # morphological analyzer
    morph = MorphAnalyzer()
    # division into sentences
    folder_path = '..' + os.sep + 'new_RuCoref_semantics'
    sentences = break_into_sentences(folder_path)
    lines_xml = lines_xml + '\n' + '<paragraphs>'
    # create <source> and all inside
    for sentence in sentences:
        lines_xml = lines_xml + '\n' + '<paragraph id=\"%d\">' % paragraph_count
        paragraph_count += 1
        lines_xml = lines_xml + '\n' + '<sentence id=\"%d\">' % sentence_count
        sentence_count += 1
        source = source_from_sentence(sentence)
        lines_xml = lines_xml + '\n' + source
        lines_xml = lines_xml + '\n' + grammar_tags(sentence, word_count, morph)
        lines_xml = lines_xml + '\n' + '</sentence>'
        lines_xml = lines_xml + '\n' + '</paragraph>'
    # ending tags
    lines_xml = lines_xml + '\n' + '</paragraphs>'
    lines_xml = lines_xml + '\n' + '</text>'


if __name__ == '__main__':
    main()