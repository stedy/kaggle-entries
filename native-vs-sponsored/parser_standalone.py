import nltk
import os
from lxml.html.clean import Cleaner
import lxml.html
from BeautifulSoup import BeautifulSoup as bs
import re
import textmining
import pandas as pd
import string
from nltk.corpus import stopwords
import argparse

train_data = pd.read_csv('train_v2.csv')
cohort = list(train_data['file'])

spons = train_data[train_data.sponsored == 1]['file']
native = train_data[train_data.sponsored == 0]['file']

#infiles = os.listdir("all_data")
#infiles = [x for x in infiles if x in cohort]

spons_tdm = textmining.TermDocumentMatrix()
organic_tdm = textmining.TermDocumentMatrix()

parser = argparse.ArgumentParser()
parser.add_argument('textfile', help = '''textfile with list of interest''')
args = parser.parse_args()

infiles = open(args.textfile)
infiles = [x.rstrip("\n") for x in infiles]

exclude = [list(string.letters), list(string.punctuation),
                list(string.whitespace), list(string.digits),
                        stopwords.words('english')]
exclude_list = [item for sublist in exclude for item in sublist]
exclude_list.append('')


for iff in infiles:
    wordslist = []
    with open("all_data/" + iff, 'rb') as temp:
        soup = bs(temp)
        if len(soup) > 0:
            if soup.find('title') is not None:
                title = soup.find('title').contents[0]

            body = soup.findAll('p')
            cleaner = Cleaner()
            cleaner.remove_tags = ['p']
            for x in body:
                document = lxml.html.document_fromstring(str(x))
                wordslist.append(document.text_content())

            wordslist = [re.sub("\\n",'',word) for word in wordslist]
            wordslist = [word.split(' ') for word in wordslist]
            wordslist = [item for sublist in wordslist for item in sublist]
            wordslist2 = []
            for word in wordslist:
                try:
                    word = word.translate(None, string.punctuation.translate(None, '"')).lower()
                    wordslist2.append(word)
                except TypeError:
                    pass
            wordslist = [word for word in wordslist2 if word not in set(exclude_list)]
            text = ""
            for word in wordslist:
                text = text +" "+ word
            if iff in set(spons):
                spons_tdm.add_doc(text)
            if iff in set(native):
                organic_tdm.add_doc(text)

spons_tdm.write_csv('spons_tdm' + str(args.textfile) + '.csv', cutoff=1)
organic_tdm.write_csv('organic_tdm' + str(args.textfile) + '.csv', cutoff=1)
