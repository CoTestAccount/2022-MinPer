import os
import json

import gensim
from gensim import corpora, models
import string
from gensim.test.utils import datapath
from gensim.utils import simple_preprocess
from gensim.matutils import corpus2dense, corpus2csc
from gensim.parsing.preprocessing import STOPWORDS

from sklearn import cluster
from sklearn import metrics

from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
np.random.seed(2018)
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

service_file = "/Users/***/Documents/Code/overclaim_tap/database/channel_info_cleaned.txt"
topic_folder = "topic_LDA/"


def print_trigger(trigger, f):
    if len(trigger) == 0:
        return
    
    #f.write("Trigger\n")
    for ele in trigger:
        f.write(ele["name"] + "\n")
        #f.write(ele["description"] + "\n")
    

def print_query(query, f):
    if len(query) == 0:
        return
    #f.write("Query\n")
    for ele in query:
        f.write( ele["name"] + "\n")
        #f.write( ele["description"] + "\n")

def print_action(action, f):
    if len(action) == 0:
        return
    #f.write("Action\n")
    for ele in action:
        f.write( ele["name"] + "\n")
        #f.write( ele["description"] + "\n")


def lowercase(input):
  """
  Returns lowercase text
  """
  return input.lower()

def remove_punctuation(input):
  """
  Returns text without punctuation
  """
  return input.translate(str.maketrans('','', string.punctuation))

def remove_whitespaces(input):
  """
  Returns text without extra whitespaces
  """
  return " ".join(input.split())

def tokenize(input):
  """
  Returns tokenized version of text
  """
  return word_tokenize(input)

def remove_stop_words(input):
  """
  Returns text without stop words
  """
  input = word_tokenize(input)
  return [word for word in input if word not in stopwords.words('english')]

def lemmatize(input):
  """
  Lemmatizes input using NLTK's WordNetLemmatizer
  """
  lemmatizer=WordNetLemmatizer()
  input_str=word_tokenize(input)
  new_words = []
  for word in input_str:
    new_words.append(lemmatizer.lemmatize(word))
  return ' '.join(new_words)


def nlp_pipeline(input):
  """
  Function that calls all other functions together to perform NLP on a given text
  """
  return lemmatize(' '.join(remove_stop_words(remove_whitespaces(remove_punctuation(lowercase(input))))))

def get_topic(score):
    max_s = 0
    re = ""
    for t in score:
        s = t[1]
        if s > max_s:
            max_s = s
            re = t[0]
    return re


def get_channel_id_name(f):
    channel_id_name = dict()
    lines = open(f, "r").readlines()
    for line in lines:
        tks = line.replace("\n", "").split(" ")
        channel_id_name[tks[0]] = tks[len(tks)-1]
    return channel_id_name



def generate_topic_doc():
  lines = open(service_file, "r").readlines()
  for line in lines:
    channel = json.loads(line)["data"]["channel"]
    if type(channel) == type(None):
        continue
    if "id" not in channel:
        continue
    c_id = channel["id"]
    f_out = open(topic_folder + c_id + ".txt", "w")
    
    ###### set services(channel) name and description as document 
    #f_out.write(channel["name"] + "\n")
    #f_out.write(channel["description"] + "\n")
    #f_out.close()

    if "triggers" in channel:
        print_trigger(channel["triggers"], f_out)
    
    if "queries" in channel:
        print_query(channel["queries"], f_out)

    if "actions" in channel:
        print_action(channel["actions"], f_out)

def train_lda_model():
  files = os.listdir(topic_folder)
  processed_doc = list()
  doc_channel_name = dict()

  meaning = []

  id_name_file = "/Users/***/Documents/Code/overclaim_tap/database/channel_id_name.txt"
  channel_id_name = get_channel_id_name(id_name_file)

  for file in files:
      path = topic_folder + file
      text = open(path, "r").read()
      words = []
      for word in text.split(' '):
          words.append(word)
      doc = nlp_pipeline(text)
      tks = doc.split(" ")
      processed_doc.append(tks)
      #doc_channel_name[doc] = file.replace(".txt", "")

      id_ = file.replace(".txt", "")
      meaning.append(channel_id_name[id_])


  ## demo for processed doc
  dictionary = gensim.corpora.Dictionary(processed_doc)
  num_docs = dictionary.num_docs
  num_terms = len(dictionary.keys())

  # bags of words
  bow_corpus = [dictionary.doc2bow(doc) for doc in processed_doc]

  # #tf idf
  tf_idf = models.TfidfModel(bow_corpus)
  corpus_tfidf = tf_idf[bow_corpus]

  corpus_tfidf_dense = corpus2dense(corpus_tfidf, num_terms, num_docs)

  # train  a cluster model

  ## first version n_cluster is 70
  ## second version n_cluster is 30 in order to better visualize

  kmeans_model = cluster.KMeans(n_clusters=10)
  kmeans_model.fit_predict(corpus_tfidf_dense.T)


  topic_services = dict()
  for index, ele in enumerate(kmeans_model.labels_):
    key = meaning[index]

    if ele not in topic_services:
      topic_services[ele] = []
    topic_services[ele].append(key)

  for cluster_name in topic_services:
    print(cluster_name, topic_services[cluster_name])

  # # train lda model using bags of words
  # #lda_model = gensim.models.ldamodel.LdaModel(bow_corpus, num_topics=40)
  # # train lda model using tf-idf
  # lda_model = gensim.models.ldamodel.LdaModel(corpus_tfidf, num_topics=70)


  # topic_services = dict()
  # for doc in doc_channel_name:
  #     bow = dictionary.doc2bow(doc.split(" "))
  #     doc_topic = get_topic(lda_model.get_document_topics(bow))
      
  #     if doc_topic not in topic_services:
  #         topic_services[doc_topic] = []
  #     topic_services[doc_topic].append(doc_channel_name[doc])



  # ## visual test demo
  # print("please input a topic number (range from 0 to 70)")

  # for topic in sys.stdin:
  #     services = topic_services[int(topic.replace("\n", ""))]
  #     print(services)
  #     for s in services:
  #       name = "https://ifttt.com/" + s
  #       webbrowser.open_new_tab(name)



if __name__ == "__main__":
  '''
  if first start, need to create topic_folder under current folder and uncomment line 245: generate_topic_doc()
  '''
  # generate_topic_doc()  
  train_lda_model()











