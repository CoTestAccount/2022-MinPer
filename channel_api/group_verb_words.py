
from operator import pos
from click import group
from nltk.corpus import wordnet as wn
import enchant

d = enchant.Dict("en_US")

def is_english_word(word):
    return d.check(word)

def is_verb(word):
    pos_l = set()
    for tmp in wn.synsets(word):
        if tmp.name().split('.')[0] == word:
            pos_l.add(tmp.pos())
        
    if 'v' in pos_l:
        return True
    return False

def word_similarity(word1):
    verb1 = wn.synsets(word1)
    print(word1, verb1)

   

def test_demo():

    word_similarity('read')
    word_similarity('see')
    word_similarity('view')
    word_similarity('edit')
    word_similarity('modify')
    word_similarity('change')
    word_similarity('delete')
    word_similarity('remove')


if __name__ == '__main__':
    test_demo()
