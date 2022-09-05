from os import sync
import requests
import json


# app_id_1 = "67ffb9a5"
# app_key_1 = "5ff47982323fab844701e78c48b2246a"

# app_id_2 = "41869762"
# app_key_2 = "b98e393c062e564bf1028ea1954e0a29"

# app_id_3 = "d94027ef"
# app_key_3 = "38d9aa52b29bdb4f332a5a6a22e0c5ca"

app_id = "25fd8ba7"
app_key = "dae74c46d7a2b57e2a3dcdb489b22551"
language = "en"



entry_url_base = "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + language + "/"
thesaurus_url_base = "https://od-api.oxforddictionaries.com:443/api/v2/thesaurus/" + language + "/"
entry_url_base_v1 = "https://od-api-demo.oxforddictionaries.com:443/api/v1/entries/" + language + "/"
filter_field = '?lexicalCategory=verb'


def remove_duplicate(arrays):
    if type(arrays) == None:
        return []
    return list(set(arrays))

def get_thesaurus_links(r):

    if r.status_code != 200:
        return [], []
    
    r_json = r.json()
    if 'results' not in r_json:
        return [], []
    
    lexialEntries = fetch_rela_field(r_json['results'], 'lexicalEntries')
    entries = fetch_rela_field(lexialEntries, 'entries')
    senses = fetch_rela_field(entries, 'senses')
    syns = fetch_rela_field(senses, 'synonyms')
    antonyms = fetch_rela_field(senses, 'antonyms')
    syns = remove_duplicate(fetch_rela_field(syns, 'text'))
    antonyms = remove_duplicate(fetch_rela_field(antonyms, 'text'))

    return syns, antonyms

def fetch_rela_field(array, key):
    result = []
    for ele in array:
        if key in ele:
            to_add = ele[key]
            if isinstance(to_add, list):
                result.extend(to_add) 
            else:
                result.append(to_add)
    return result


def check_key_exist(ele, key):
    if key in ele:
        return True
    
    return False

def word_api_call(word_id):
    url_entry = entry_url_base + word_id.lower() + filter_field
    url_thesaurus = thesaurus_url_base + word_id.lower()
    r1 = requests.get(url_entry, headers={"app_id": app_id, "app_key": app_key})
    r2 = requests.get(url_thesaurus, headers={"app_id": app_id, "app_key": app_key})
    
    code_1 = r1.status_code

    if code_1 != 200:
        return [], []
    
    r1_json = r1.json()

    if 'results' not in r1_json:
        return [], []
    
    lexialEntries = fetch_rela_field(r1_json['results'], 'lexicalEntries')
    entries = fetch_rela_field(lexialEntries, 'entries')
    senses = fetch_rela_field(entries, 'senses')
    syns = fetch_rela_field(senses, 'synonyms')
    syns = remove_duplicate(fetch_rela_field(syns, 'text'))


    similar, atonyms = get_thesaurus_links(r2)
    syns.extend(similar)
    
    syns = remove_duplicate(syns)
    atonyms = remove_duplicate(atonyms)

    return syns, atonyms


if __name__ == '__main__':
    syns, atonyms = word_api_call('change')
    print('syns: ', syns)
    print('atonyms: ', atonyms)