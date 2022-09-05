'''
A sample code usage of the python package stanfordcorenlp to access a Stanford CoreNLP server.
Written as part of the blog post: https://www.khalidalnajjar.com/how-to-setup-and-use-stanford-corenlp-server-with-python/ 
'''


## how to start a server:  in ~/Document/CoreNLP
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer  -preload tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation  -status_port 9000 -port 9000 -timeout 15000''



from __future__ import annotations
from cgitb import text
from stanfordcorenlp import StanfordCoreNLP
import json

class StanfordNLP:
    pos_dict = {
        'CC': 'coordinating conjunction','CD': 'cardinal digit','DT': 'determiner',
        'EX': 'existential there (like: \"there is\" ... think of it like \"there exists\")',
        'FW': 'foreign word','IN':  'preposition/subordinating conjunction','JJ': 'adjective \'big\'',
        'JJR': 'adjective, comparative \'bigger\'','JJS': 'adjective, superlative \'biggest\'',
        'LS': 'list marker 1)','MD': 'modal could, will','NN': 'noun, singular \'desk\'',
        'NNS': 'noun plural \'desks\'','NNP': 'proper noun, singular \'Harrison\'',
        'NNPS': 'proper noun, plural \'Americans\'','PDT': 'predeterminer \'all the kids\'',
        'POS': 'possessive ending parent\'s','PRP': 'personal pronoun I, he, she',
        'PRP$': 'possessive pronoun my, his, hers','RB': 'adverb very, silently,',
        'RBR': 'adverb, comparative better','RBS': 'adverb, superlative best',
        'RP': 'particle give up','TO': 'to go \'to\' the store.','UH': 'interjection errrrrrrrm',
        'VB': 'verb, base form take','VBD': 'verb, past tense took',
        'VBG': 'verb, gerund/present participle taking','VBN': 'verb, past participle taken',
        'VBP': 'verb, sing. present, non-3d take','VBZ': 'verb, 3rd person sing. present takes',
        'WDT': 'wh-determiner which','WP': 'wh-pronoun who, what','WP$': 'possessive wh-pronoun whose',
        'WRB': 'wh-abverb where, when','QF' : 'quantifier, bahut, thoda, kam (Hindi)','VM' : 'main verb',
        'PSP' : 'postposition, common in indian langs','DEM' : 'demonstrative, common in indian langs'
    }

    def __init__(self, host='http://localhost', port=9000):
        self.nlp = StanfordCoreNLP(host, port=port,
                                   timeout=30000)  # , quiet=False, logging_level=logging.DEBUG)
        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json',
            'prettyPrint': False,
        }

    def word_tokenize(self, sentence):
        return self.nlp.word_tokenize(sentence)

    def pos(self, sentence):
        return self.nlp.pos_tag(sentence)

    def ner(self, sentence):
        return self.nlp.ner(sentence)

    def parse(self, sentence):
        return self.nlp.parse(sentence)

    def dependency_parse(self, sentence):
        return self.nlp.dependency_parse(sentence)

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))
    

    @staticmethod
    def tokens_to_dict(_tokens):
        tokens = defaultdict(dict)
        for token in _tokens:
            tokens[int(token['index'])] = {
                'word': token['word'],
                'lemma': token['lemma'],
                'pos': token['pos'],
                'ner': token['ner']
            }
        return tokens


be_verb = ["be", "am", "are", "is"]
others_verb = ["do", "let", "like", "may", "maybe", "want", "forget", "wish", "have",
            "allow", "include",

]
special_verbs = ["access", "share", "upload", "see", "edit", "read", "view", "control", "reprogram", "delete"]
special_nouns = ["device", "profile"]
black_list_nouns = ['application', 'ifttt', 'account', 'access', 'permission']

nn_marks = ["NNP", "NNS", "NN", "NNPS"]
verb_marks = ["VB", "VBZ", "VBD", "VBN", "VBP","VBG"]



def format_sentence(sentence):

    #### remove heading and tailing space
    #### turn all to lower case
    sentence = sentence.replace("\n", "").replace('’', '\'')
    sentence = sentence.lower()
    sentence = sentence.strip()

    ### remove non alpha heading
    ### remove digital or other heading
    pos = 0
    for i in range(0, len(sentence)):
        if sentence[i].isalpha():
            pos = i
            break
    
   
    sentence = sentence[pos:]
    return sentence


def parse_sentence_noun(sentence):
            sentence = format_sentence(sentence)
            sNLP = StanfordNLP()
            annotations = sNLP.annotate(sentence)["sentences"][0]
            tokens = annotations["tokens"]

            # print("parse sentence noun: ", tokens)
            tks_number = len(tokens)
            potential_nn = []
            visited = set()

            for tk in tokens:
                index = tk["index"] - 1 ## index start from 1
                if index in visited:
                    continue
                if tk["pos"] in nn_marks and tk['lemma'] not in black_list_nouns:
                    words = [tk["lemma"]]
                    visited.add(index)
                    
                    ## connect all the neighbor nn together
                    for j in range(index+1, tks_number):
                        neighbor_tk = tokens[j]
                        if neighbor_tk["pos"] in nn_marks:
                            words.append(tokens[j]["lemma"])
                            visited.add(j) 
                        else:
                            break

                    potential_nn.append(' '.join(words))
            return potential_nn


def parse_sentence_veb(sentence):
    sentence = format_sentence(sentence)
    sNLP = StanfordNLP()
    annotations = sNLP.annotate(sentence)["sentences"][0]
    verbs = []
    potential = []

    tokens = annotations["tokens"]
    for tk in tokens:
        if tk["pos"] == 'VB' or tk['pos'] == 'VBP' or tk['pos'] == 'VBZ':         
            verbs.append(tk["lemma"])

    first_word = sentence.split()[0]
    if first_word not in verbs:
        potential.append(first_word)
    return verbs, potential

def cut_head_sentence(tokens, service_name):
    #print("#########################################################")
    pos, lemma = "pos", "lemma"
    verb_position = 0
    count = 0 
    for tk in tokens:
        count = count + 1
        if tk[lemma] in special_verbs:
            #print("found first verb: ", tk["word"])
            verb_position = count
            break
        if tk[pos] not in verb_marks:
            continue
        if tk[pos] in verb_marks and ( tk[lemma] in be_verb or tk[lemma] in others_verb):
            continue

        ## this word in is verb, not be_verb or like_verb -> which means it's the first verb we found
        if verb_position == 0:
            #print("found first verb: ", tk["word"])
            verb_position = count
            break
    
    noun_followed, your_found, nnp_found, spec_nn_found = False, False, False, False
    new_sentence = ""
    for i in range(count-1, len(tokens)):
        tk = tokens[i]
        new_sentence += " "
        new_sentence += tk["word"] 
        if tk[pos] in nn_marks:
            #print("found nnp or nn: ", tk["word"])
            noun_followed = True
        if tk["word"] == "your" or tk["word"] == "you":
            #print("found word your: ", tk["word"])
            your_found = True
        if (tk[pos] in nn_marks) and (tk[lemma] in service_name):
            #print("found nnp similar to service name: ", tk["word"])
            nnp_found = True

        if (tk[lemma] in special_nouns):
            #print("found special nn like: ", tk[lemma])
            spec_nn_found = True

    
    if verb_position > 0 and noun_followed and (your_found or nnp_found or spec_nn_found):
        return new_sentence, True
    return new_sentence, False




def preprocess_verb_noun_pair(sentence, service_name):
    sentence = format_sentence(sentence)
    sNLP = StanfordNLP()
    annotations = sNLP.annotate(sentence)["sentences"][0]
    enhanced_dep = annotations["enhancedDependencies"]
    tokens = annotations["tokens"]

    cutted_sentence, found = cut_head_sentence(tokens, service_name)
    if found == False:
        #print("failed:", sentence)
        return sentence, False
    else:
        # print("success",cutted_sentence)
        return cutted_sentence, True


def sent_annotation(sentence):
    sent = format_sentence(sentence)
    sNLP = StanfordNLP()
    annos = sNLP.annotate(sent)
    return annos


def sent_tokens_word(sentence):
    sent = format_sentence(sentence)
    sNLP = StanfordNLP()
    annos = sNLP.annotate(sent)["sentences"][0]
    tokens = annos["tokens"]
    results = []

    for tk in tokens:
        results.append(tk['word'])
    return results

if __name__ == '__main__':
    text = 'add file to Google Drive at the path you specify.'
    text = 'download a file at a given URL and add it to OneDrive at the path you specify.'
   # text = 'remove your litter robot\'s sleep schedule.'
    print(parse_sentence_verb_obj_pair(text))
    
