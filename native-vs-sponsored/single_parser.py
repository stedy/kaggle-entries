from lxml.html.clean import Cleaner
import lxml.html
from BeautifulSoup import BeautifulSoup as bs
import re
import textmining
import argparse
from nltk.corpus import stopwords
import string

parser = argparse.ArgumentParser(description="""Single file checker""")
parser.add_argument('infile', help = "path to file of interest")
args = parser.parse_args()

tdm = textmining.TermDocumentMatrix()

exclude = [list(string.letters), list(string.punctuation),
                        list(string.whitespace), list(string.digits),
                                                stopwords.words('english')]
exclude_list = [item for sublist in exclude for item in sublist]
exclude_list.append('')

word_list = []
with open(args.infile, 'rb') as infile:
    soup = bs(infile)
    if len(soup) > 0:
        if soup.find('title') is not None:
            title = soup.find('title').contents[0]
            print title
        body = soup.findAll('p')
        print body
        cleaner = Cleaner()
        cleaner.remove_tags = ['p']
        for x in body:
            document = lxml.html.document_fromstring(str(x))
            word_list.append(document.text_content())

        word_list = [re.sub("\\n", '', word) for word in word_list]
        word_list = [word.split(' ') for word in word_list]
        word_list = [item for sublist in word_list for item in sublist]

        wordslist2 = []
        for word in word_list:
            try:
                word = word.translate(None,string.punctuation.translate(None,'"')).lower()
                wordslist2.append(word)
            except TypeError:
                pass
        word_list = [word for word in wordslist2 if word not in set(exclude_list)]

        text = ""
        for word in word_list:
            text = text +" "+ word
        tdm.add_doc(text)

print word_list
