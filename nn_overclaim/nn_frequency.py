## purpose of this file: 
## calculate the word frequency in different service group to help filter out some common 
##   nn like "permission", "third party app"
from curses.ascii import isalpha
import sys 
import os
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/stanford_parser")
from stanford_parser import parse_sentence_noun


word_document_frequency = dict()
word_group_frequency = dict()
group_services = dict() ## key is group id, value is a list of service name
service_group = dict() ## key is service name, value is group id

def load_services_group(v=None):
    group_services, service_group
    cluster_file = "/Users/***/Documents/Code/overclaim_tap/channel_api/channel_cluster/lda_cluster.txt"
    if (v == None) == False:
        cluster_file = "/Users/***/Documents/Code/overclaim_tap/channel_api/channel_cluster/lda_cluster_" + str(v) + ".txt"
    lines = open(cluster_file, "r")
    for line in lines:
        tks  = (line.replace(" ", "").replace("[", ",").replace("]","").replace("'","").replace('\n', '')).split(",")
        if len(tks) < 2:
            continue
        group_services[tks[0]] = tks[1:]

        for service in tks[1:]:
            service_group[service] = tks[0]
    return group_services, service_group

def add_count(nn, word_document_frequency):
    #global word_document_frequency
    if nn in word_document_frequency:
        word_document_frequency[nn] = word_document_frequency[nn] + 1
    else:
        word_document_frequency[nn] = 1
    return

def is_empty_line(line):
    str = ""
    for s in line:
        if isalpha(s):
            str += s
    if len(str) == 0:
        return True
    return False

def process_service(lines, service_name):
    nouns = []
    for line in lines:
        if len(line) > 1000 or is_empty_line(line):
            continue # filter out too long sentence
        nouns.extend(parse_sentence_noun(line))
    
    nouns = set(nouns)
    for nn in nouns:
        add_count(nn, word_document_frequency)

def process_service_in_group(lines, group):
    nouns = []
    for line in lines:
        if len(line) > 1000 or is_empty_line(line):
            continue # filter out too long sentence
        nouns.extend(parse_sentence_noun(line))
    
    nouns = set(nouns)
    for nn in nouns:
        add_count(nn, word_group_frequency)

def process_all_services():
    auth_folder = "/Users/***/Documents/Code/overclaim_tap/oauth/fetch_OAuth_info/auth_log/"
    files = os.listdir(auth_folder)
    for f in files:
        path = auth_folder + f 
        lines = open(path, "r")
        process_service(lines, f)

def print_word_frequency():
    global word_document_frequency
    for w in sorted(word_document_frequency, key=word_document_frequency.get, reverse=True):
        print(w, word_document_frequency[w])

if __name__ == "__main__":
    process_all_services()
    print_word_frequency()   

        
