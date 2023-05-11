'''
A sample code usage of the python package stanfordcorenlp to access a Stanford CoreNLP server.
Written as part of the blog post: https://www.khalidalnajjar.com/how-to-setup-and-use-stanford-corenlp-server-with-python/ 
'''


## how to start a server:  in ~/Document/CoreNLP
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer  -preload tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation  -status_port 9000 -port 9000 -timeout 15000''



from __future__ import annotations
from cgi import test

from stanfordcorenlp import StanfordCoreNLP
import json
from nltk.tree import Tree
from nltk.tree import ParentedTree
import sys

sys.path.insert(1, '../stanford_parser')
from load_finfo import load_permission_info




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
            'prettyPrint': True,
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
    "allow", "include", "authorize", "grant", "connect", 
]
others_noun = ['ifttt', 'applets', 'login', 'password', 'integration', 'term']

special_verbs = ["access", "share", "upload", "see", "edit", "read", "view", "control", "reprogram", "delete", "read"]
special_nouns = ["device", "profile"]

nn_marks = ["NNP", "NNS", "NN", "NNPS"]
verb_marks = ["VB", "VBZ", "VBD", "VBN", "VBP","VBG"]
verb_strict_mark = ['VB', 'VBP', 'VBZ']


## variable used for global purpose
vp_sents = []
np_sents = []


benchmark_mode = False
debug_mode = False

def format_sentence(sentence):

    #### remove heading and tailing space
    #### turn all to lower case
    sentence = sentence.replace("\n", "")
    sentence = sentence.lower()
    sentence = sentence.strip()

    ## remove dashs, check-ins, power-up -> checkins, powerup
    tks = sentence.split(' ')
    new_tks = []
    for tk in tks:
        if '-' not in tk:
            new_tks.append(tk)
        else:
            new_tks.append(tk.replace('-', ''))
    sentence = ' '.join(new_tks)

    ### remove non alpha heading
    ### remove digital or other heading
    pos = 0
    for i in range(0, len(sentence)):
        if sentence[i].isalpha():
            pos = i
            break
    
    
    sentence = sentence[pos:]
    if len(sentence) == 0:
        return sentence
        
    if sentence[-1].isalpha(): ## add ending com
        sentence += ' .'
    return sentence


def get_sentence_header_tail(original_sent, middle_sent):
    tks = original_sent.split(middle_sent)
    return tks[0], tks[len(tks)-1]

def split_conj_character(sent, vp_np):
    sent = sent.replace("/", ", ")
    tks = sent.split(",")
    ## after split, we found that some verb's obj is missing -> use the nearest right verb;s obj
    return tks


def replace_pronoun_with_noun(coref, tokens):
    refer_text = ''

    result = []

    prp_to_replace = ['it', 'they']
    coref_flat = dict()

    for group in coref:
        entityes = coref[group]
        for entity in entityes:
            coref_flat[entity['id']] = entity

    for tk in tokens:
        word = tk['word']
        if tk['pos'] == 'PRP' and tk['lemma'] in prp_to_replace:
            prp_ind = tk['index']
            ## find if this word has coref in relationship:
            for id in coref_flat:
                ele = coref_flat[id]
                start_ind = ele['startIndex']
                end_ind = ele['endIndex']
                if start_ind == prp_ind and end_ind == prp_ind + 1:
                    ## found
                    potential_pos = ele['position']
                    for ppos in potential_pos:
                        if ppos == ele['id']:
                            continue
                        refer_text = coref_flat[ppos]['text']
                        break
            if refer_text != '':
                word = refer_text
        result.append(word)
    return ' '.join(result)


to_replace_words = {
    'see': 'read',
    'view': 'read',
    'edit': 'modify',
    'delete': 'remove',
    'access': 'read',
    'update': 'modify',
    'share': 'distribute',
}

def replace_word(text):
    tokens = text.lower().split()
    result = []

    for tk in tokens:
        if tk in to_replace_words:
            result.append(to_replace_words[tk])
        else:
            result.append(tk)
    return ' '.join(result)


def pre_process_atomic_sentence(text):
    text = replace_word(text)
    if '/' not in text: ## spilt the whole sentence in /
        return [text]
    
    back_up = text  ## remove space near the /
    while(' /' in back_up):
        back_up = back_up.replace(' /', '/')
    while('/ ' in back_up):
        back_up = back_up.replace('/ ', '/')
    
    result = []
    tks = back_up.split(' ')


    for inde, tk in enumerate(tks):
        if '/' in tk:
            words = tk.split('/')
            header = ' '.join(tks[:inde])
            tail = ' '.join(tks[inde + 1:])
            for word in words:
                sep = [header, word, tail]
                result.append(' '.join(sep))
    return result


def parse_sentence_obl(sentence):
    sNLP = StanfordNLP()
    sentence = format_sentence(sentence)
    annotations = sNLP.annotate(sentence)
    if check_dep_exist(annotations) == False:
        return ''
    
    enhanced_plus_plus_dep = annotations['sentences'][0]['enhancedPlusPlusDependencies']
    tokens = annotations['sentences'][0]['tokens']

    verb_index = -1
    for tk in tokens:
        pos = tk['pos']
        if pos in ['VB', 'VBP', 'VBZ']:
            #print("found first vb: ", tk['lemma'])
            verb_index = tk['index']
            break

    obl_index, obl_dep = -1, ''
    obj_index = -1
    for dep in enhanced_plus_plus_dep:
        govern = dep['governor']
        dep_rela = dep['dep']

        if govern == verb_index  and 'obj' in dep_rela:
            obj_index = dep['dependent']
        if govern == verb_index  and 'obl' in dep_rela:
            obl_index = dep['dependent']
            obl_dep = dep_rela.replace('obl:', '') 
            break
    result_tks = []
    if obl_index > -1:
        if obj_index > -1:
            for tk in tokens[obj_index + 1 : obl_index + 1]:
                result_tks.append(tk['word'])
        else:
            result_tks = [tokens[obl_index-1]['word']]
    
    if obj_index > -1 and obl_index == -1:
        for tk in tokens[obj_index + 1:]:
            if tk['pos'] in nn_marks:
                result_tks.append(tk['word'])

    return ' '.join(result_tks)


def check_parse_exit(anno):
    if 'sentences' not in anno:
        return False
    if len(anno['sentences']) == 0:
        return False
    
    if 'parse' not in anno['sentences'][0]:
        return False
    
    return True


def check_dep_exist(anno):
    if 'sentences' not in anno:
        return False
    if len(anno['sentences']) == 0:
        return False
    if 'enhancedPlusPlusDependencies' not in anno['sentences'][0]:
        return False
    return True

def check_token_exist(anno):
    if 'sentences' not in anno:
        return False
    if len(anno['sentences']) == 0:
        return False
    if 'tokens' not in anno['sentences'][0]:
        return False
    return True


def capture_core_kernel_noun(noun):
    sNLP = StanfordNLP()
    annotations = sNLP.annotate(noun)
    tokens = annotations['sentences'][0]['tokens']

    result_tokens = []
    for tk in reversed(tokens):
        pos = tk['pos']
        if pos in nn_marks:
            result_tokens.append(tk['lemma'])
        
        if len(result_tokens) > 0 and pos not in nn_marks:
            break
    if len(result_tokens) == 0:
        return noun
    return ' '.join(result_tokens)


def contains_substr(substr_array, str):
    for substr in substr_array:
        if substr in str:
            return True
    return False

def find_appos_related_noun(enhanced_plus_plus_dep, noun_indexs):
    appos_nouns = []
    for dep in enhanced_plus_plus_dep:
        govern = dep['governor']
        dep_rela = dep['dep']

        if govern in noun_indexs and 'appos' in dep_rela:
            appos_nouns.append(dep['dependentGloss'])
    return appos_nouns

def parse_sentence_verb_obj_pair(sentence):
    sentence = replace_word(format_sentence(sentence))
    pairs = parse_sentence_verb_obj_pair_detail(sentence)
    if len(pairs) > 0:
        return pairs
    pairs = parse_sentence_verb_obj_pair_detail(sentence.capitalize())
    return pairs

def parse_sentence_verb_obj_pair_detail(sentence):
    global debug_mode
    #sentence = replace_word(format_sentence(sentence))
    #print('in parse_sentence: ', sentence)
    sNLP = StanfordNLP()
    annotations = sNLP.annotate(sentence)
    if check_dep_exist(annotations) == False:
        return

    sentence = replace_pronoun_with_noun(annotations['corefs'], annotations['sentences'][0]['tokens'])
    
    annotations = sNLP.annotate(sentence)
    enhanced_plus_plus_dep = annotations['sentences'][0]['enhancedPlusPlusDependencies']
    tokens = annotations['sentences'][0]['tokens']


    verb_indexs = []
    verb_obj_indexs = dict() # key is verb index, value the is corresponding obj index (of this verb) 
    verb_obl_indexs = dict()
    obl_dep = ''

    for tk in tokens:
        pos = tk['pos']
        if pos in verb_strict_mark and (tk['lemma'] not in others_verb and tk['lemma'] not in be_verb):
            #print("found first vb: ", tk['lemma'])
            verb_indexs.append(tk['index'])
            verb_obj_indexs[tk['index']] = -1
            continue
        if tk['lemma'] in special_verbs:
            verb_indexs.append(tk['index'])
            verb_obj_indexs[tk['index']] = -1

    obj_indexs, obl_indexs = [], []
    for dep in enhanced_plus_plus_dep:
        govern = dep['governor']
        dep_rela = dep['dep']

        if govern in verb_indexs and 'obj' in dep_rela:
            verb_obj_indexs[govern] = dep['dependent']
            obj_indexs.append(dep['dependent'])

        if govern in verb_indexs and 'obl' in dep_rela:
            verb_obl_indexs[govern] = dep['dependent'] 
            #obl_dep = dep_rela.replace('obl:', '')
            obl_indexs.append(dep['dependent'])
    
    results = []

    obj_appos = find_appos_related_noun(enhanced_plus_plus_dep, obj_indexs)

    for verb_ind in verb_obj_indexs:
        obj_ind = verb_obj_indexs[verb_ind]
        verb = tokens[verb_ind - 1]['lemma']

        obj_tks = []
        for ind in range(verb_ind, obj_ind):
            obj_tks.append(tokens[ind]['word'])
        if len(obj_tks) == 0:
            continue
        obj = capture_core_kernel_noun(' '.join(obj_tks))
        #obj = ' '.join(obj_tks)
        if contains_substr(others_noun, obj) == False:
            results.append((verb, obj))
            for appos_noun in obj_appos:
                results.append((verb, appos_noun))
    
    if len(results) == 0 and bool(verb_obl_indexs):
        for verb_ind in verb_obl_indexs:
            obl_ind = verb_obl_indexs[verb_ind]
            verb = tokens[verb_ind - 1]['word']
            obl = capture_core_kernel_noun(tokens[obl_ind - 1]['lemma'])
            #obl = tokens[obl_ind - 1]['lemma']
            if contains_substr(others_noun, obl) == False:
                results.append((verb, obl))

    return results


def post_process_atomic_sentence(texts):
    sNLP = StanfordNLP()

    result = []
    np_obj = ' '
    global debug_mode

    
    for text in reversed(texts):
        anno = sNLP.annotate(text)
        if check_parse_exit(anno) == False:
            continue
        tree_str = anno['sentences'][0]['parse']
        if debug_mode:
            visualize(tree_str)
        t = Tree.fromstring(tree_str)

        tree_with_parent = ParentedTree.convert(t)
        found_np = False
        for sub_tree in tree_with_parent.subtrees():
            if sub_tree._label == 'VP':
                words = []
                base_tree = sub_tree
                for sub_sub_tree in base_tree.subtrees():
                    if sub_sub_tree._label == 'NP':
                        while(sub_sub_tree):
                            words.extend(sub_sub_tree.leaves())
                            sub_sub_tree = sub_sub_tree.right_sibling()
                        
                        found_np = True
                        np_obj = ' '.join(words)

                        if debug_mode:
                            print('np_obj: ', np_obj)
                        ## must break, other wise it would dive down to include repeat phrase
                    if found_np:
                        break
            if found_np:
                break

        if found_np == False:
            text = text.replace(' .', '') + ' ' + np_obj
        
        result.append(text)
    if debug_mode:
        print('post process result: ', result)
    return list(reversed(result))

        


def concan_header_tail(header, middle, tail):
    result = header
    
    if len(result) > 0:
        result = result + ' ' + middle
    else:
        result = middle
    
    if len(tail) == 0 or tail == '.':
        result += tail
    else:
        result = result + ' ' + tail
    return result


def atomic_sentence(text, np_vp):
    ## only proceed one cc each time
    ## otherwise, the format would become complex to deal with
    sNLP = StanfordNLP()
    sentence = format_sentence(text)
    anno = sNLP.annotate(text)
    if check_parse_exit(anno) == False:
        return [], False

    tree_str = anno['sentences'][0]['parse']
    t = Tree.fromstring(tree_str)
    tree_with_parent = ParentedTree.convert(t)
    leaves = tree_with_parent.leaves()

    sentence = ' '.join(leaves)

    result = []
    neighbor_before_conj = []
    found_cc = False

    global debug_mode
    for sub_tree in tree_with_parent.subtrees():

        if sub_tree._label == "CC" and sub_tree.parent()._label == np_vp:
            found_cc = True
            base_node = sub_tree

            tokens = []
            while base_node.left_sibling():
                sibling = base_node.left_sibling()
                base_node = sibling
                if sibling.parent()._label == np_vp:
                    leaves = sibling.leaves()
                    tokens.append(' '.join(leaves))
            
            tokens = ' '.join(reversed(tokens)).split(',')
            neighbor_before_conj.extend(tokens)

            base_node = sub_tree

            nn_obj = []
            while base_node.right_sibling():
                sibling = base_node.right_sibling()
                base_node = sibling
                if sibling._label == 'NP' and np_vp == 'VP':
                    while(sibling):
                        leaves = sibling.leaves()
                        nn_obj.extend(leaves)   
                        sibling = sibling.right_sibling()
                    break
                if sibling.parent()._label == np_vp:
                    leaves = sibling.leaves()
                    neighbor_before_conj.append(' '.join(leaves))
            
            if len(nn_obj) > 0:
                last_ele = neighbor_before_conj[-1]
                neighbor_before_conj[-1] = last_ele + ' ' + ' '.join(nn_obj)
            
            # find the obj for this vp
            
            if np_vp == 'VP':
                neighbor_before_conj = post_process_atomic_sentence(neighbor_before_conj)
            middle_sent_origin = ' '.join(sub_tree.parent().leaves())
            header, tail = get_sentence_header_tail(sentence, middle_sent_origin)

            if debug_mode == True:
                print("middle_sent: ", middle_sent_origin)
                print("neighbor before conf: ", neighbor_before_conj)
            
            for neighbor in neighbor_before_conj:
                if len(neighbor) == 0:
                    continue
                result.append(concan_header_tail(header, neighbor, tail))
            ## only break once for each atomatic
            break

    
    if len(result) == 0 or found_cc == False: ## if no conj word found, return original text directly
        return [text], False
    #result = post_process_atomic_sentence(result)
    return result, True



def dfs_search(sent, vp_np):
    global vp_sents, np_sents
    results, found_cc = atomic_sentence(sent, vp_np)
    if found_cc == False and vp_np == 'VP':
        vp_sents.extend(results)
        return
    
    if found_cc == False  and vp_np == 'NP':
        np_sents.extend(results)
        return

    if found_cc == True:
        for result in results:
            dfs_search(result, vp_np)

    return



def remove_dup_list_ele(lists):
    set_t = set(lists)
    return list(set_t)

def parse_Constituency_Parse_Tree(sent):
    ### always split and that connect verb first 
    ### then split and that connect noun second

    global vp_sents, np_sents
    vp_sents, np_sents = [], []
    sNLP = StanfordNLP()
    sent = format_sentence(sent)
    anno = sNLP.annotate(sent)

    ## preprocess the sentence to 
    sent = replace_pronoun_with_noun(anno['corefs'], anno['sentences'][0]['tokens'])
    sents = pre_process_atomic_sentence(sent)

    ## process the verb firstly
    ## dfs algorithm
    for sent in sents:
        dfs_search(sent, 'VP')
    
    vp_sents = remove_dup_list_ele(vp_sents)

    for sent in vp_sents:
        dfs_search(sent, 'NP')
    
    np_sents = remove_dup_list_ele(np_sents)

    return remove_dup_atomatic(np_sents)


def visualize(tree_str):
    t = Tree.fromstring(tree_str)
    print(t.pretty_print())
    return

def visualize_tree_structure(text):
    sNLP = StanfordNLP()
    anno = sNLP.annotate(text)
    tree_str = anno['sentences'][0]['parse']
    t = Tree.fromstring(tree_str)
    tree_with_parent = ParentedTree.convert(t)
    visualize(tree_str)

    for sub_tree in tree_with_parent.subtrees():
        if sub_tree._label == 'CC':
            base_node = sub_tree
            while(base_node.right_sibling()):
                sibling = base_node.right_sibling()
                print("############## sibling")
                print("right sibling label: ",sibling._label)
                print("right sibling parent label: ", sibling.parent()._label)
                print("right sibling node: ", sibling.leaves())
                #print(base_node.right_sibling())
                base_node = base_node.right_sibling()
            base_node = sub_tree
            while(base_node.left_sibling()):
                sibling = base_node.left_sibling()
                print("############## sibling")
                print("left sibling label: ", sibling._label)
                print("left sibling parent label: ", sibling.parent()._label)
                print("left sibling node: ", sibling.leaves())
                base_node = base_node.left_sibling()
    return


def remove_dup_atomatic(sents):
    sents = remove_dup_list_ele(sents)

    result = []
    for ele in sents:
        filtered = False
        for ele2 in sents:
            if ele in ele2 and len(ele2) > len(ele):
                filtered = True
        
        if filtered == False:
            tks = [tok for tok in ele.split(' ') if tok]
            result.append(' '.join(tks))
    return result


def main_atomic():
    info = load_permission_info()

    for service_name in info:
        print("service name: ", service_name)
        permissions = info[service_name]
        for permission in permissions:
            results = parse_Constituency_Parse_Tree(permission)

            print("###############")
            for result in results:
                print(result)
        print("###############")


def test_to_be_delete():
    sentence = 'create new tips and check-ins.'
    sents = parse_Constituency_Parse_Tree(sentence)
    print(sents)
    

if __name__ == "__main__":
    # txts = [ 
    #   "read scenes and timer status and execute/enable/disable them.",
    #   "retrieve your chatroom's messages, tasks, files, notes and member information.",
    #     # change access to retrieve
    #  'Execute a scene and enable/disable a timer.',
    #  'Create, modify, and remove posts, comments, and reactions on your behalf.',
    #  'read, modify, create, and remove all of your Google Drive files',
    #  'modify content of your Dropbox files and folders, read content of your Dropbox files and folders, and modify and read information about your Dropbox files and folders',
    #  'IFTTT will be able to create new pages but cannot read or modify existing pages.',
    #  'IFTTT  cannot read or modify existing pages on your behalf.',

    #  'See the names and emails of people you share your spreadsheets with.',
    #  'Read and write your app data, including projects, tasks, notes, labels, and filters.',
    #  'Granting access will let IFTTT detect and control your wemos and anything that is connected to them.',
    #  'Delete notebooks and tags',
    #  'IFTTT is requesting access to a BeoLiving Intelligence, if you proceed we will link this service to your BeoLiving Intelligence and it will get access to: ifttt',
    # ]
    
    # # #for txt in txts:
    # if True:
    #     txt = 'distribute  or public your SpotCam video.'
    #     
    #     #txt = 'read scenes and timer status and execute/enable/disable them.'
    #     result = parse_Constituency_Parse_Tree(txt)
    #     print('fininal result: ',txt, result)
    

    #test_to_be_delete()

    debug_mode = False
    benchmark_mode = True
    main_atomic()



   
    
