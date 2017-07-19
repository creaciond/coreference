from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import requests
import re
import unicodedata


def texts(url):
    '''
        FUNCTION texts(url): returns a text via url
        TAKES: url (str)
        RETURNS: clean_text(str), new line = new paragraph
    '''
    #! settings
    clean_text = ''
    # text only in <tr></tr>
    texts_tag = SoupStrainer('tr')
    #! get only text
    response = requests.get(url)
    text = BeautifulSoup(response.text, 'html.parser', parse_only=texts_tag).get_text()
    #! work with text
    # remove non-stretching spaces
    newline_for_paragraph = unicodedata.normalize('NFKD', text)
    # split into paragraphs
    lines_into_paragraphs = re.sub('[0-9]+? [0-9]+?\.', '\n', newline_for_paragraph)
    original_texts = [line for line in lines_into_paragraphs.split('\n') if line != '']
    # get rid of sentence numbers
    for par in original_texts:
        if clean_text != '':
            clean_text = clean_text + '\n' + (re.sub('\.?[0-9]+?\.', '', par)).strip(' ')
        else:
            clean_text = (re.sub('\.?[0-9]+?\.', '', par)).strip(' ')
    return clean_text


def main():
    text_ids = []
    with open('./opencorpora_text_ids.tsv', 'r', encoding='utf-8') as f_ids:
        for line in f_ids.readlines():
            items = line.split('\t')
            text_ids.append(int(items[0]))
    for text_id in text_ids:
        url = 'http://opencorpora.org/books.php?book_id={}&full=1'.format(text_id)
        try:
            par = texts(url)
            print(par)
        except:
            print('error: {}'.format(text_id))


if __name__ == '__main__':
    main()