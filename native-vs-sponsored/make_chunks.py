import pandas as pd
train = pd.read_csv('train_v2.csv')
cohort = list(train['file'])

def chunks(l,n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

cohort_cut = list(chunks(range(1,len(cohort)), len(cohort)/40))

counter = 0
for l in cohort_cut:
    with open("listset_" + str(counter) + ".txt", 'wb') as of:
        files = [cohort[x] for x in l]
        for x in files:
            of.write("%s\n" % x)
    counter += 1
