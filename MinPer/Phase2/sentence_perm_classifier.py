import numpy as np, pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import confusion_matrix, accuracy_score
sns.set() # use seaborn plotting style
import random



def load_sentence_labels():
    f = 'sent_class.csv'
    sentences = []
    labels = []
    lines = open(f, 'r').readlines()
    random.shuffle(lines)
    for line in lines:
        lable = line[0]
        sent = line[2:].replace('\"', '')
        print(lable, sent)
        sentences.append(sent)
        labels.append(lable)
    return sentences, labels

def split_dataset():
    sents, labels = load_sentence_labels()
    index = int(0.8 * len(sents))
    train_data, train_labels = sents[:index], labels[:index]
    test_data, test_labels = sents[index:], labels[index:]

    return train_data, train_labels, test_data, test_labels


def classify():
    train_d, train_l, test_d, test_l = split_dataset()

    # Build the model
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    # Train the model using the training data
    model.fit(train_d, train_l)
    # Predict the categories of the test data
    predicted_categories = model.predict(test_d)

    print("The accuracy is {}".format(accuracy_score(test_l, predicted_categories)))

if __name__ == "__main__":
    classify()
