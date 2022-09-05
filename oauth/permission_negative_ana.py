from curses.ascii import isalpha
import os
from pydoc import doc
import sys
from tracemalloc import stop
from regex import F
import spacy
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
sys.path.insert(1, '/Users/***/Documents/Code/overclaim_tap/stanford_parser')
from atomic_operation import parse_sentence_verb_obj_pair

auth_folder = "/Users/***/Documents/Code/overclaim_tap/oauth/fetch_OAuth_info/auth_log/"
nlp = spacy.load("en_core_web_md")
pos_permissions = [
    nlp('ifttt will be able to'), nlp('ifttt would like to'), 
    nlp('it will be able to'), nlp('com will be able to'),

    nlp('this application would like to'),  nlp('this application can'),
    nlp('this application will be able to'),

    nlp('this app wants permission to'),
    nlp('this app will be able to'), nlp('this app would like to'),

    nlp('this application wants to have'),


    nlp('this will allow'), nlp('this will allow ifttt to'),
    nlp('this will allow the developer of ifttt to'),

    nlp('by authorizing this link, you \'ll allow ifttt to:'),
]

require_permissions = [
    nlp('ifttt request full access to your account'),
    nlp('ifttt would like to access the following'),
    nlp('authorize ifttt to have access to'),
    nlp('allow ifttt to connect to your'),
    nlp('ifttt would like to access your account'),
    nlp('ifttt is requesting access to'),
    nlp('you grant this app the following permissions'),
    nlp('ifttt is requesting access to your account'),
    nlp('ifttt has requested access to'),
    nlp('ifttt is requesting access to your account'),
    nlp('application requires the following permissions'),
    nlp('ifttt will be using the following data'),
    nlp('by logging in you indicate that you agree to grant ifttt access'),
    nlp('ifttt asks you to grant the following permissions'),
    nlp('grant https : //ifttt.com/ access to your'),
    nlp('grant ifttt access to your account'),
    nlp('authorize ifttt access'),
    nlp('by authorizing this link , you \'ll allow ifttt to :'),
]

neg_permissions = [
    nlp('ifttt will not be able to'), nlp('com will not be able to'), 
    nlp('this application will not be able to'), nlp('it will not be able to'),
    nlp('this application cannot'),
    nlp('ifttt will not have permission to'),

]


neg_info_without_body = [
    "will not be able to",
    "will not allow",
]
## detect files has such format: ifttt would like to/ ifttt would not

test_services = ['pocket', 'flickr', 'evernote', 'spotcam', 'wink_shortcuts', 'medium', 'trello', 'timelines','facebook_pages', 'discord', 'fiverr', 'nomos_system', 'tecan_connect']
#test_services = ['timelines', 'facebook_pages']

def cos_sim(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

def load_raw_sentences():
    sentences = []
    auth_logs = os.listdir(auth_folder)
    for log in auth_logs:
        path = auth_folder + log
        lines = open(path, "r").readlines()
        sentences.extend(lines)
    
    tokenized_sent = []
    for s in sentences:
        s = s.replace("\n", "")
        tokenized_sent.append(word_tokenize(s.lower()))
    return tokenized_sent


def fetch_neg_permissions(lines):
    #print(lines)
    result = []
    for ind, line in enumerate(lines):
        pairs = parse_sentence_verb_obj_pair(line)
        #print(pairs)
        if len(pairs) == 0 and ind == 0:
            continue

        if len(pairs) == 0 and ind > 0:
            break
        result.append(line)
    #print(result)
    return result


def doc2vec(tokenized_sent):
    tagged_data = [TaggedDocument(d, [' '.join(d)]) for _, d in enumerate(tokenized_sent)]
    model = Doc2Vec(tagged_data, vector_size = 20, window = 2, min_count = 1, epochs = 100)

    test_doc = word_tokenize("ifttt will not be able to".lower())
    test_doc_vector = model.infer_vector(test_doc)
    demo = model.docvecs.most_similar(positive = [test_doc_vector])
    print(demo)


def format_sentence(sentence):
    tokenized = word_tokenize(sentence.replace("\n", "").lower())
    return ' '.join(tokenized)


def contains_neg_phrase(sentence):
    neg_marks = ['not',  'n\'t']
    tks = sentence.split(' ')
    for mark in neg_marks:
        if mark in tks:
            return True
    return False



def remove_end_comma(line):
    new_line = ""
    for s in line:
        if isalpha(s):
            new_line += s
        if s == ' ':
            new_line += s
    return new_line.strip()

def maybe_noise_for_grant_permission(sentence):
    tks = sentence.split(" ")
    id_marks = [" application ", "ifttt", "this app ", "this application "]
    exist_mark = False
    for mark in id_marks:
        if mark in sentence:
            exist_mark = True
    if "it" not in tks  and "com" not in tks  and exist_mark == False:
        return True
    return False

def find_neg_permission(lines_origin, file_name):

    pos, neg = False, False
    pos_sentence,neg_sentence = '', ''

    pos_index , neg_index = -1, -1

    # print("################################################")

    lines = [format_sentence(line) for line in lines_origin]
    for index ,line in enumerate(lines):
        if len(line.split(" ")) < 4:
            continue

        sentence = nlp(line)
        for pos_permission in pos_permissions:
            if pos_permission.similarity(sentence) > 0.9 and contains_neg_phrase(line) == False and maybe_noise_for_grant_permission(line) == False:
                pos_sentence = line
                pos_index = index
                pos = True

        for neg_permission in neg_permissions:
            if neg_permission.similarity(sentence) > 0.9 and contains_neg_phrase(line) == True and maybe_noise_for_grant_permission(line) == False:
                neg_sentence = line
                neg_index = index
                neg = True
    remove_com_lines = [remove_end_comma(line) for line in lines]

    for neg_info in neg_info_without_body:
        if neg_info in remove_com_lines:
            neg_sentence = neg_info

            for ind, info in enumerate(remove_com_lines):
                if info == neg_info:
                    neg_index = ind
            neg = True

    if neg_index == -1:
        return False
    #print('########', file_name, 'before fetch: ')
    #print(neg_index)
    neg_permissions_lines = fetch_neg_permissions(lines[neg_index:])
    #print('############')


    if len(neg_permissions_lines) > 0:
        print("#################### find neg pairs in ", file_name)
        print('#### contains neg permission: ')
        print('\n'.join(neg_permissions_lines))
        return True
    
    return False

def sentence_contains_mark(words, sentence):
    for word in words:
        if word in sentence:
            return word,True
    return "", False

def find_privacy(lines, file_name):
    stop_words = ['privacy']
    for index in range(len(lines)):
        sentence = format_sentence(lines[index])
        contained_word, found = sentence_contains_mark(stop_words, sentence)
        if found:
            print("############################# find ", contained_word, "#### ", file_name)
            print('\n'.join(lines[index:]))



def process_all_neg_file():
    auth_logs = os.listdir(auth_folder)
    for log in auth_logs:

        service_name = log.replace('_channels_', '').replace('__phase1', '').replace('__phase2', '')
        # print(service_name)
        if service_name not in test_services:
            continue
        if '_phase2' in log:
            path = auth_folder + log
            lines_origin = open(path, "r").readlines()
            found = find_neg_permission(lines_origin,log)

            phase1_log = log.replace('_phase2', '_phase1')
            if phase1_log in auth_logs and found ==  False:
                path = auth_folder + phase1_log
                lines_origin = open(path, "r").readlines()
                find_neg_permission(lines_origin,phase1_log)
        
        if '_phase1' in log and log.replace('_phase1', '_phase2') not in auth_logs:
            path = auth_folder + log
            lines_origin = open(path, "r").readlines()
            find_neg_permission(lines_origin,log)





if __name__ == "__main__":
    #find_privacy(lines, log)
    # tokens = load_raw_sentences()
    # doc2vec(tokens)
    process_all_neg_file()
