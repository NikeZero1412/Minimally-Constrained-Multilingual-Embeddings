import nltk
from nltk.corpus import wordnet as wn

import itertools
import random
import argparse

DATA_DIR = "E:\GIT_ROOT\\Unsupervised_taxonomy"

ENG_PATH = "path to BLESS resources\en_BLESS"
FRE_PATH = "path to BLESS resources\\fr_BLESS"
ESP_PATH = "path to BLESS resources\es_BLESS"
ITA_PATH = "path to BLESS resources\it_BLESS"

parser = argparse.ArgumentParser()
parser.add_argument("lang", help="Choose language",type=str)

args = parser.parse_args()

def ishyper(syn1,syn2):
    hyperset = set([i for i in syn1.closure(lambda s: s.hypernyms())])
    return syn2 in hyperset

def findpair(syn_list1,syn_list2):
    flag=False
    child_syn = random.choice(syn_list1)
    parent_syn = random.choice(syn_list2)
    for syn1, syn2 in itertools.product(syn_list1, syn_list2):
        if ishyper(syn1,syn2) and not flag:
            flag=True
            child_syn, parent_syn =syn1,syn2


    return flag, child_syn,parent_syn

def pad(offset):
    if len(str(offset))!=8:
        return "0"*(8-len(str(offset)))+str(offset)
    else:
        return offset

def get_synset(word):
    lemma,pos=word[:-2],word[-1]
    if pos=='j':
        pos="s"
    try:
        offsets=wn._lemma_pos_offset_map[lemma][pos]

    except KeyError:
        offsets=[syn._offset for syn in wn.synsets(lemma)]

    padding = [pad(ss) for ss in offsets]
    omw_list = [str(ss) + "-" + str(pos) for ss in padding]
    syn_list = []
    for offset in omw_list:
        syn=wn.synset("oven.n.01")
        try:
            syn = wn.of2ss(offset)
        except StopIteration:
            pass
        except AssertionError:
            pass
        except nltk.corpus.reader.wordnet.WordNetError:
            continue
        except ValueError:
            continue
        finally:
            syn_list.append(syn)


    return syn_list


def create():

    if args.lang == "fra":
        PATH = FRE_PATH
        filename = "fr_temp"

    elif args.lang == "ita":
        PATH = ITA_PATH
        filename = "it_temp"

    elif args.lang == "spa":
        PATH = ESP_PATH
        filename = "es_temp"

    with open(ENG_PATH, mode='r', encoding="utf-8") as f:
        print("Loading lines from en_BLESS file")
        data = f.read()
        lines = data.splitlines()
    with open(filename, mode='w', encoding="utf-8") as target:
        print("Writing in new BLESS file")
        for line in lines:
            print(line)
            seg = line.strip().split()
            child, parent  = seg[0], seg[1]
            child_synsets=get_synset(child)
            parent_synsets = get_synset(parent)
            if len(parent_synsets)==0:
                continue
            flag,child_syn,parent_syn=findpair(child_synsets,parent_synsets)
            child_words = [(lemma._name + "-" + lemma._synset._pos) for lemma in child_syn.lemmas(args.lang)]
            parent_words = [(lemma._name + "-" + lemma._synset._pos) for lemma in parent_syn.lemmas(args.lang)]
            if flag:
                relation, category = "True", "hyper"
            else:
                relation, category = "False", "random"
            for cw, pw in itertools.product(child_words, parent_words):
                target.write("%s \t %s \t %s \t %s\n" % (cw, pw, relation, category))

        target.close()


create()
# Run the following command to remove duplicates
# awk '!seen[$0]++' it_temp > it_BLESS
