#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jack Hester
Created February 2019
Written for "Mining Adverse Drug Effects from Online Healthcare Forum Posts"
Contact jack.hester@emory.edu
Creates, trains, and implements a support vector machine (SVM) to classify...
...extracted phrases as adverse side effect (1) or not (0)
Thanks to coding-maniac for tutorial on building SVMs...
...this partly based on that tutorial
"""

from pandas import DataFrame as df
import csv
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif, chi2

# function to train on training csv, return the accuracy based on test data and
# return the SVM to use for future prediciton
def trainer():
    # row[1] is the ngram
    ngrams = []
    # row[5] is result (whether or not is SE or not)
    results = []
    
    with open('/Users/jhester/Desktop/thesis-code/ngram-table-train.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) # we don't want tilte row
        for row in csv_reader:
           ngrams.append(row[1])
           results.append(row[5])
    csv_file.close()
           
    # get data of ngram and result columns
    raw_data = {'ngram': ngrams, 'result': results}
    
    # store important columns in pandas data frame
    data = df(data=raw_data)
     
    # a tiny bit of cleanup, just to make things smoother, incuding all lower case
    data['ngram_clean'] = data['ngram'].apply(lambda x: " ".join(i for i in re.sub("[^a-zA-Z]", " ", x).split()).lower())
    
    # test size: allocated 20% for test data, rest (80%) for training (out of 550 total)
    x_train, x_test, y_train, y_test = train_test_split(data['ngram_clean'], data.result, test_size=0.2)
    
    pipeline = Pipeline([('vect', TfidfVectorizer(ngram_range=(1,2), stop_words="english", sublinear_tf=True)),
                         ('fclas',  SelectKBest(f_classif, k=50)),
                         ('clf', LinearSVC(C=1.0, penalty='l1', max_iter=3000, dual=False))])
    
    # fit model to training data
    SVM = pipeline.fit(x_train, y_train)
    
    # getting some outputs interesting for results
    vectorizer = SVM.named_steps['vect']
    fclas = SVM.named_steps['fclas']
    #clf = SVM.named_steps['clf']
    
    feature_names = vectorizer.get_feature_names()
    feature_names = [feature_names[i] for i in fclas.get_support(indices=True)]
    feature_names = np.asarray(feature_names)
    
    #top 5 keywords used in finding 0 (neg) or 1 (pos)
    # =============================================================================
    # target_names = ['0', '1']
    # print("top five keywords per class:")
    # for i, label in enumerate(target_names):
    #     top5 = np.argsort(clf.coef_[i])[-5:]
    #     print("%s: %s" % (label, " ".join(feature_names[top5])))
    # =============================================================================
    accuracy = SVM.score(x_test, y_test)
    #return accuracy, fscore, SVM
    return accuracy, SVM
    #print("accuracy score: " + str(accuracy))

# function to generate the predictions (fill isSE column) on input csv
def generatePrediction(SVM):
    #with open('/Users/jhester/Desktop/thesis-code/ngram-table.csv', 'r') as unlabeled_csv:
    with open('/Users/jhester/Desktop/thesis-code/new-drug-ngram-table.csv') as unlabeled_csv:
        csv_reader = csv.reader(unlabeled_csv)
        #next(csv_reader) # we don't want tilte row
        with open('/Users/jhester/Desktop/thesis-code/new-drug-ngram-table-complete.csv', 'w+') as output_csv:
            csv_writer = csv.writer(output_csv)
            next(csv_reader)
            csv_writer.writerow({'','ngram','drug','date','filename','isSE'})
            for row in csv_reader:
                #if row!=550:
                currGram = row[1]
                currResult = SVM.predict([currGram])
                resultStr = str(currResult)
                resultStr  = resultStr.split("\'")[1]
                #resultStr  = resultStr.split("\']")[0]
                row[5] = resultStr
                csv_writer.writerow(row)
                
accuracy, SVM = trainer()
print('Accuracy of this run:', str(accuracy))
#print('Finished writing predictions to provided file(s)')
