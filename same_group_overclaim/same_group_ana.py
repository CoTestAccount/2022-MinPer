## purpose of this file
#try to capture the overclaim under same group

import sys
from tkinter.tix import Tree
sys.path.insert(1, '/Users/***/Documents/Code/overclaim_tap/nn_overclaim')
from nn_frequency import load_services_group
sys.path.insert(1, '/Users/***/Documents/Code/overclaim_tap/stanford_parser')
from atomic_operation import parse_sentence_verb_obj_pair
sys.path.insert(1, '/Users/***/Documents/Code/overclaim_tap/verb_overclaim')
from overclaim_detection import similar_operator_operand, load_atomic_permission


debug_mode = False
service_lda_group = dict()
lda_group_services = dict()

neg_services_list = ['pocket', 'flickr', 'evernote', 'spotcam', 'wink_shortcuts', 'medium', 'trello', 'timelines','facebook_pages', 'discord', 'fiverr', 'nomos_system', 'tecan_connect']

#neg_services_list = ['spotcam']

def fetch_negtive():
    service_neg_permission = dict()
    file = '/Users/***/Documents/Code/overclaim_tap/oauth/permission_detail_ana/negative_permission.txt'
    service_name = ''
    permissions = []


    lines = open(file, 'r').readlines()
    for line in lines:
        if 'find neg pairs in' in line:
            if len(permissions) > 0:
                service_neg_permission[service_name] = permissions
            service_name = line.replace('#################### find neg pairs in  _channels_', '').replace('__phase2', '').replace('__phase1', '').replace('\n', '')
            permissions = []
            continue
        if 'contains neg permission:' in line:
            continue

        permissions.append(line)
    
    if len(permissions) > 0:
        service_neg_permission[service_name] = permissions
    return service_neg_permission


def identify_similar_permission(perms_not_allowed, perms_allowd_other_services):
    potential_filtered = []
    for perm_neg in perms_not_allowed:
        pairs_neg = parse_sentence_verb_obj_pair(perm_neg)
        if len(pairs_neg) == 0 or len(pairs_neg[0]) == 0 :
            continue
        for perm_pos in perms_allowd_other_services:
            pairs_pos = parse_sentence_verb_obj_pair(perm_pos)

            for pair_pos in pairs_pos:
                if similar_operator_operand(pair_pos, pairs_neg):
                    potential_filtered.append(perm_pos)
    return  potential_filtered





def identify_same_group(neg_service, same_group_services, permissions, neg_permissions):
    for same_group_service in same_group_services:
        if same_group_service not in permissions or same_group_service == neg_service or neg_service not in neg_permissions:
            continue

        if debug_mode:
            print('compare to services: ', same_group_service)

        potential_sim = identify_similar_permission(neg_permissions[neg_service], permissions[same_group_service])
        if len(potential_sim) > 0:
            print('neg service: ', neg_service, 'compared service: ', same_group_service, '##', potential_sim)
    return


def test_main():
    lda_group_services, service_lda_group = load_services_group()
    ## key is service name, value the the lad_group this service belong
    ## key is ldagroup number, value is the services that this permission belong to
    atomic_permission = load_atomic_permission()

    neg_permissions = fetch_negtive()
    for service in neg_services_list:

        if debug_mode == True:
            print('begin to service: ', service)
        identify_same_group(service, lda_group_services[service_lda_group[service]], atomic_permission, neg_permissions)

    return
if __name__ == '__main__':
    debug_mode = True
    test_main()


    ## end of main function



