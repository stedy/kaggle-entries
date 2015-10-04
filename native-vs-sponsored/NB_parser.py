import nltk
import os
from lxml.html.clean import Cleaner
import lxml.html
from BeautifulSoup import BeautifulSoup as bs
import re
import textmining
import pandas as pd
import pickle
import string
from nltk.corpus import stopwords

train_data = pd.read_csv('train_v2.csv')
cohort = list(train_data['file'])

spons = train_data[train_data.sponsored == 1]['file']
native = train_data[train_data.sponsored == 0]['file']

infiles = os.listdir("all_data")
infiles = [x for x in infiles if x in cohort]

spons_tdm = textmining.TermDocumentMatrix()
organic_tdm = textmining.TermDocumentMatrix()

counter = 0
for iff in infiles:
    wordslist = []
    with open("all_data/" + iff, 'rb') as temp:
        counter += 1
        print counter/len(infiles)
        soup = bs(temp)
        if len(soup) > 0:
            if soup.find('title') is not None:
                title = soup.find('title').contents[0]
            print iff
            body = soup.findAll('p')
            cleaner = Cleaner()
            cleaner.remove_tags = ['p']
            for x in body:
                document = lxml.html.document_fromstring(str(x))
                wordslist.append(document.text_content())

            wordslist = [re.sub("\\n",'',word) for word in wordslist]
            wordslist = [word.split(' ') for word in wordslist]
            wordslist = [item for sublist in wordslist for item in sublist]
            wordslist = [word.translate(None,
                string.punctuation.translate(None, '"')).lower() for word in wordslist]
            wordslist = [word for word in wordslist if word not in stopwords.words()]
            text = ""
            for word in wordslist:
                text = text +" "+ word
            if iff in set(spons):
                spons_tdm.add_doc(text)
            if iff in set(native):
                organic_tdm.add_doc(text)

pickle.dump(spons_tdm, open('spons_tdm.pkl', 'wb'))
pickle.dump(organic_tdm, open('organic_tdm.pkl', 'wb'))
spons_tdm.write_csv('spons_tdm.csv', cutoff=1)
organic_tdm.write_csv('organic_tdm.csv', cutoff=1)
