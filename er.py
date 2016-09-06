import nltk
import string
from nltk.tag import StanfordNERTagger
from nltk import pos_tag
from nltk.chunk import conlltags2tree
from nltk.tree import Tree
from collections import Counter
from nltk.corpus import stopwords

# http://stackoverflow.com/questions/30664677/extract-list-of-persons-and-organizations-using-stanford-ner-tagger-in-nltk
# Converts Stanford's NER output to BIO format
def stanfordNE2BIO(tagged_sent):
    bio_tagged_sent = []
    prev_tag = "O"
    for token, tag in tagged_sent:
        if tag == "O": #O
            bio_tagged_sent.append((token, tag))
            prev_tag = tag
            continue
        if tag != "O" and prev_tag == "O": # Begin NE
            bio_tagged_sent.append((token, "B-"+tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag == tag: # Inside NE
            bio_tagged_sent.append((token, "I-"+tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag != tag: # Adjacent NE
            bio_tagged_sent.append((token, "B-"+tag))
            prev_tag = tag
    return bio_tagged_sent

# also from the same StackOverflow link
# Converts Stanford's NER output to BIO format, and then an NLTK tree from that
def stanfordNE2tree(ne_tagged_sent):
    bio_tagged_sent = stanfordNE2BIO(ne_tagged_sent)
    sent_tokens, sent_ne_tags = zip(*bio_tagged_sent)
    sent_pos_tags = [pos for token, pos in pos_tag(sent_tokens)]
    sent_conlltags = [(token, pos, ne) for token, pos, ne in zip(sent_tokens, sent_pos_tags, sent_ne_tags)]
    ne_tree = conlltags2tree(sent_conlltags)
    return ne_tree

# also from the same StackOverflow link
def getEntityListFromTree(ne_tree):
    ne_in_sent = []
    for subtree in ne_tree:
        if type(subtree) == Tree: # If subtree is a noun chunk, i.e. NE != "O"
            ne_label = subtree.label()
            ne_string = " ".join([token for token, pos in subtree.leaves()])
            ne_in_sent.append((ne_string, ne_label))
    return ne_in_sent

def getListOfEntities(tagged_sent):
    ne_tree = stanfordNE2tree(tagged_sent) # construct a tree
    ne_in_sent = getEntityListFromTree(ne_tree) # traverse the tree and build list of entities
    return ne_in_sent

def getEntities(text):
    if text:
        print("Text: %s" % text)

        # NLTK config
        nltk.data.path.append('./nltk_data/')

        # split the body of text into words
        tokenized_sent = nltk.word_tokenize(text)

        # recognize named entities from tokens
        res = st.tag(tokenized_sent)

        # The following function converts the default output from Stanford NER,
        # which displays compound entities (e.g. Hillary Clinton or Apple Inc) as
        # separate entities when the words are right next to each other. The code it
        # calls is all from stackoverflow (linked in the comments).
        entities = getListOfEntities(res)

        print("Entities: %s" % entities)
        return entities
    return None

st = StanfordNERTagger('stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')
