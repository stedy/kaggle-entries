import pandas as pd
from scrapy.selector import Selector
import os
import re
import string
from nltk.corpus import stopwords
import numpy as np
import textmining
import math

exclude = [list(string.letters), list(string.punctuation),
           list(string.whitespace), list(string.digits),
           stopwords.words('english')]
exclude_list = [item for sublist in exclude for item in sublist]
exclude_list.append('')

train_data = pd.read_csv('train_v2.csv')
cohort = list(train_data['file'])

#spons = train_data[train_data.sponsored == 1]['file']
#native = train_data[train_data.sponsored == 0]['file']

path = os.path.abspath('all_data')

spons = os.listdir("all_data")[0:10]
#spons = ['10836_raw_html.txt', '10686_raw_html.txt', '10674_raw_html.txt']
spons = [os.path.join(path, x) for x in spons]
native = ['10632_raw_html.txt', '10302_raw_html.txt', '10290_raw_html.txt']
native = [os.path.join(path, x) for x in native]

def get_msg(infile):
    with open(infile, 'rb') as iff:
        words = []
        sel = Selector(text=iff.read())
        for x in sel.xpath("//title/text()").extract():
            words.append(re.findall("[a-z0-9']+", x.lower()))
        for y in sel.xpath("//p/text()").extract():
            words.append(re.findall("[a-z0-9']+", y.lower()))
        words = [item for sublist in words for item in sublist]
        final = [word for word in words if word not in exclude_list]
        text = ' '.join(final)
        return text

def get_msgdir(msglist):
    return [get_msg(f) for f in msglist]

all_spons = get_msgdir(spons)
all_organic = get_msgdir(native)

def tdm_df(doclist):
    tdm = textmining.TermDocumentMatrix()
    for doc in doclist:
        tdm.add_doc(doc)
    tdm_rows, occurrence = [], []
    for rows in tdm.rows():
        tdm_rows.append(rows)

    tdm_array = np.array(tdm_rows[1:])
    tdm_terms = tdm_rows[0]
    
    df = pd.DataFrame(tdm_array, columns = tdm_terms)
    return df

spons_tdm = tdm_df(all_spons)
organic_tdm = tdm_df(all_organic)

def make_term_df(df):
    occurrence = []
    term_df = pd.DataFrame({"term":df.columns.values, "frequency":df.sum(0)})

    for x in df.columns.values:
        occurrence.append(float(sum([y != 0 for y in df[x]]))/len(df.index))

    term_df['occurrence'] = occurrence
    term_df['density'] = term_df['frequency'] / sum(term_df['frequency'])
    return term_df

spons_term_df = make_term_df(spons_tdm)
organic_term_df = make_term_df(organic_tdm)

def classify_email(msg, training_df, prior = 0.5, c = 1e-6):
    msg_tdm = tdm_df(msg)
    msg_freq = msg_tdm.sum()
    msg_match = list(set(msg_freq.index).intersection(set(training_df.index)))
    if len(msg_match) < 1:
        return math.log(prior) + math.log(c) * len(msg_freq)
    else:
        match_probs = training_df.occurrence[msg_match]
        return (math.log(prior) + np.log(match_probs).sum() + math.log(c) *
                (len(msg_freq) - len(msg_match)))

test = [os.path.join(path,x) for x in os.listdir("all_data")]

def classifier(msglist):
    spons_probs = [classify_email(m, spons_term_df) for m in get_msgdir(test)]
    native_probs = [classify_email(m, organic_term_df) for m in get_msgdir(test)]
    classify = np.where(np.array(spons_probs) > np.array(native_probs),0,1)
    out_df = pd.DataFrame({'pr_spons' : spons_probs,
        'pr_organic' : native_probs,
        'classify': classify},
        columns = ['pr_spons', 'pr_organic', 'classify'])
    return out_df

print classifier(test)
