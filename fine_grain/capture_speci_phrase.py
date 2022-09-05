
import json
import sys
import itertools
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/stanford_parser")
from stanford_parser import StanfordNLP, parse_sentence_noun
sys.path.insert(1, '/Users/***/Documents/Code/overclaim_tap/channel_api/')
from channel_api_ana import text_split
sys.path.insert(1, '/Users/***/Documents/Code/overclaim_tap/nn_overclaim/')
from nn_overclaim_det import is_nn_similarity



'''
want to find more? can refer to this one 
https://universaldependencies.org/u/dep/index.html



acl: clausal modifier of noun
acl:relcl: relative clause modifier
advcl: adverbial clause modifier
advmod: adverbial modifier
amod: adjectival modifier
appos: appositional modifier
aux: auxiliary
auxpass: passive auxiliary
case: case marking
cc: coordination
cc:preconj: preconjunct
ccomp: clausal complement
compound: compound
compound:prt: phrasal verb particle
conj: conjunct
cop: copula
csubj: clausal subject
csubjpass: clausal passive subject
dep: dependent
det: determiner
det:predet: predeterminer
discourse: discourse element
dislocated: dislocated elements
dobj: direct object
expl: expletive
foreign: foreign words
goeswith: goes with
iobj: indirect object
list: list
mark: marker
mwe: multi-word expression
name: name
neg: negation modifier
nmod: nominal modifier
nmod:npmod: noun phrase as adverbial modifier
nmod:poss: possessive nominal modifier
nmod:tmod: temporal modifier
nsubj: nominal subject
nsubjpass: passive nominal subject
nummod: numeric modifier
parataxis: parataxis
punct: punctuation
remnant: remnant in ellipsis
reparandum: overridden disfluency
root: root
vocative: vocative
xcomp: open clausal complement


'''

verb_mark = ['VB', 'VBP', 'VBZ']


### align with the preprocess in # channel_api_ana.py
trigger_heads = [
        "this trigger fires when", 
        "this trigger fires every time when", 
        "this trigger fires every time", 
        "this trigger fires",

        "this trigger fire every time",



        "the trigger fires every time",
        "the trigger fires when",


        "this triggers fires when",
        "this triggers fires every time",
        "this triggers when",

        "triggers when",
        "triggered when",

        "this trigger is fired every time",
        "this trigger is fired when",
        "this trigger is triggered when",

        "this trigger will fire every time",
        "this trigger will fires when",
        "this trigger runs every time",
        "this trigger works when",
        

        "this trigger when",
        "this triggers fire every time",
        "this trigger",
    ]

query_heads = [
        "this query returns",
        "return",
        "returns",


        "a query that returns",
        "the query returns",


        "this query returns"
        "this query will return",
        "this querys returns",
        "this query lists",
        "this query searches",

        "query",

    ]

action_heads = [
        "this action will",
        "the action will",
    ]

middle_header = itertools.chain(trigger_heads, query_heads, action_heads)
headers = list(middle_header)

def remove_header(description):
    process_des = description.lower()
    for head in headers:
        if process_des.startswith(head):
            process_des = process_des.replace(head, " ", 1)
            return process_des.lstrip()
    return process_des.lstrip()





def fetch_params(fields):
    potential_names = []
    for field in fields:
        label = field['label']
        slug = field['slug']
        name = field['name']
        potential_names.extend([label,slug, name])
    modified_name = []
    for ele in potential_names:
        if ele: # not null
            modified_name.append(' '.join(text_split(ele)))

    modified_name = list(set(modified_name))
    return modified_name

    

    
    
    
def check_field_exist(field_name, json_obj):
    content = json_obj[field_name]
    if content == None:
        return False
    if len(content) == 0:
        return False
    return True

def get_service_api_description():
    file_path = '/Users/***/Documents/Code/overclaim_tap/oauth/channel_info_cleaned.txt'
    lines = open(file_path, "r").readlines()


    ## for now, reserve the triggers and queries, only tested on actions
    services_triggers = dict()
    services_queries = dict()


    services_actions = dict()

    for line in lines:
        json_obj = json.loads(line)['data']['channel']
        service_name = json_obj['name']

        if check_field_exist('actions', json_obj) == False:
            continue

        actions = json_obj['actions']
        actions_name = []

        for action in actions:
            if check_field_exist('description', action) == False:
                continue
            


            description = remove_header(action['description'])
            params = fetch_params(action['action_fields'])

            infos = []
            infos.append(description)
            infos.extend(params)


            actions_name.append(infos)
        
        services_actions[service_name] = actions_name
    return services_actions



def check_dep_exist(anno):
    if 'sentences' not in anno:
        return False
    if len(anno['sentences']) == 0:
        return False
    if 'enhancedPlusPlusDependencies' not in anno['sentences'][0]:
        return False
    return True



def anno_ana(annotations):
    if check_dep_exist(annotations) == False:
        return ''

    enhanced_plus_plus_dep = annotations['sentences'][0]['enhancedPlusPlusDependencies']
    tokens = annotations['sentences'][0]['tokens']

    verb_index = -1
    for tk in tokens:
        pos = tk['pos']
        if pos in verb_mark:
            print("found first vb: ", tk['lemma'])
            verb_index = tk['index']
            break

    obl_index, obl_dep = -1, ''
    obj_index = -1
    nmod_index = -1
    for dep in enhanced_plus_plus_dep:
        govern = dep['governor']
        dep_rela = dep['dep']

        if govern == verb_index  and 'obj' in dep_rela:
            obj_index = dep['dependent']
        if govern == verb_index  and 'obl' in dep_rela:
            obl_index = dep['dependent']
            obl_dep = dep_rela.replace('obl:', '') 
            break

        if obj_index > 0 and govern == obj_index and ('nmod' in dep_rela or 'obl' in dep_rela):
            nmod_index = dep['dependent'] 
    
    result_tks = []

    print('obj: ', obj_index, 'obl: ', obl_index, 'nmod: ', nmod_index)

    result1, result2 = '' ,''
    if obl_index > 0:
        if obl_dep != '':
            result_tks = [obl_dep]
        for tk in tokens[obl_index - 1:]:
            result_tks.append(tk['word'])
        result1 =' '.join(result_tks)

    if nmod_index > 0:
        for tk in tokens[obj_index : max(nmod_index, len(tokens) + 1)]:
            result_tks.append(tk['word'])
        result2 = ' '.join(result_tks)
    
    
    if result1 in result2:
        return result2
    else:
        return result1




    ## find the direct obj for this verb

    ## for this obj, find the following acl or nmod (word)


    ## continue this loop until find all the following

    ## whether this should be fine gained or change context (whether it define file name and path at the same time)

    ## if this is a change context: like 'add a row' or 'append a row' would follow by 'to XXX' but exclue 'to google drive' 'to one drive such kind of info'
   


def compare_similarity_params(poten_fine_grained, params):
    fine_grained_nn = parse_sentence_noun(poten_fine_grained)
    if len(fine_grained_nn) == 0 :
        return ''

    print('nn for specified part: ', fine_grained_nn[0])
    for param in params:
        if is_nn_similarity(fine_grained_nn[0], param):
            return param
    return ''

def test_main():
    service_action = get_service_api_description()
    sNLP = StanfordNLP()
    ## key is service name, value is a list of actions [des, para1, para2]
    for service in service_action:
        print('####### service name:', service)
        actions = service_action[service]
        for action in actions:
            des = action[0]
            params = action[1:]

            annos = sNLP.annotate(des)
            fine_grained = anno_ana(annos)
            similar_param = ''

            if len(fine_grained) > 0:
                similar_param = compare_similarity_params(fine_grained, params)
            if len(fine_grained) > 0 and similar_param != '':
                print( 'fine grained: ', fine_grained, '##### sim params: ', similar_param)
                print('original sentence: ', des)
    




if __name__ == '__main__':


    test_main()
    # text = 'append to a text file as defined by the file name and folder path you specify.'
    # #text = 'add a single row to the bottom of the first worksheet of a spreadsheet you specify.'
    # #text = 'add file to Google Drive at the path you specify.'
    # #text = 'create a new text file at the path you specify.'
    # # text = 'create a new text note in a folder with tags you specify.'
    # # text = 'download a file at a given URL.'
    # text = 'download a file at a given URL and add it to Google Drive at the path you specify.'
    # '''
    # example:
    # append to a text file as defined by the file name and folder path you specify.
    # add a single row to the bottom of the first worksheet of a spreadsheet you specify.
    # download a file at a given URL and add it to Google Drive at the path you specify.
    # '''

    # print(text)
    # sNLP = StanfordNLP()
    # annos = sNLP.annotate(text)
    # fine_grained_scope = anno_ana(annos)
    # print(fine_grained_scope)

