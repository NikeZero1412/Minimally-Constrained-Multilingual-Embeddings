
# coding: utf-8

# In[2]:


import os
import numpy as np
import nltk, re, pprint
import django
import codecs
from gensim import models
from django.utils.encoding import smart_str
from bs4 import BeautifulSoup
from nltk import tokenize
from random import shuffle
import ujson
import gensim
import numpy as np
#from libraries.acs import acs

# In[ ]:

from gensim.parsing import PorterStemmer
global_stemmer = PorterStemmer()
 
class StemmingHelper(object):
    """
    Class to aid the stemming process - from word to stemmed form,
    and vice versa.
    The 'original' form of a stemmed word will be returned as the
    form in which its been used the most number of times in the text.
    """
 
    #This reverse lookup will remember the original forms of the stemmed
    #words
    word_lookup = {}
 
    @classmethod
    def stem(cls, word):
        """
        Stems a word and updates the reverse lookup.
        """
 
        #Stem the word
        stemmed = global_stemmer.stem(word)
 
        #Update the word lookup
        if stemmed not in cls.word_lookup:
            cls.word_lookup[stemmed] = {}
        cls.word_lookup[stemmed][word] = (
            cls.word_lookup[stemmed].get(word, 0) + 1)
 
        return stemmed
 
    @classmethod
    def original_form(cls, word):
        """
        Returns original form of a word given the stemmed version,
        as stored in the word lookup.
        """
 
        if word in cls.word_lookup:
            return max(cls.word_lookup[word].keys(),
                       key=lambda x: cls.word_lookup[word][x])
        else:
            return word


# In[33]:

# Path to the Language Wiki Corpii

ENG_DIR = os.path.join(os.getcwd(),"data/English_Wiki")
ESP_DIR = os.path.join(os.getcwd(),"wikiextractor/Spanish_Wiki")
FRE_DIR = os.path.join(os.getcwd(),"wikiextractor/French_Wiki")
ITA_DIR = os.path.join(os.getcwd(),"wikiextractor/Italian_Wiki")

# File list in each directory

ENG_filenames=os.listdir(ENG_DIR)
ESP_filenames=os.listdir(ESP_DIR)
FRE_filenames=os.listdir(FRE_DIR)
ITA_filenames=os.listdir(ITA_DIR)

def preprocess(content):
    """
    Function that preprocesses the data 
    
    (1) Parses through html/xml content and removes it
    (2) Sets words to lowercase
    (3) Sentence Tokenization
    (4) Word Tokenization and Lemmatization
    
    Parameters: Content read from the file
    Returns : List of sentences 
    """
    soup = BeautifulSoup(content, 'html.parser')
    data = soup.get_text().lower()
    sentences=tokenize.sent_tokenize(data.lower())
    for i in range(len(sentences)):
        sentences[i]=sentences[i].split()
    return sentences
    
    
    
def parsecorpus(mode,DIR,filename,n):
    """
    Input parameters:
        1) mode - "Save"/"Load" depending on what you want to do
        2) DIR - Path to the corpus        
        3) filename - 'abc.json', any name to pickle your corpus and save or load it.
                       Must be present in the same location, else change the code to find the file
        4) n - number of files to load in each subdirectory of the wiki corpus        
    """
    
    
    # Global list variable for corpus sentences after processing
    LAN_sentences = []
    if mode=="Load":
        # Reading data back
       print "Loading Languge"
       with open(filename, 'r') as f:
             LAN_sentences = ujson.load(f)
       f.close()
       print "Language Loaded" 	
  
    print "Done with Language"
    if mode=="Save":
        print "Going through the Wiki"
        for subdir, dirs, files in os.walk(DIR):
            for file in files[::n]:
                with codecs.open(os.path.join(subdir,file),'rb',encoding='utf-8') as doc:
                    content =doc.read()
                    LAN_sentences += preprocess(content)
        # Random shuffle of the sentences
        shuffle(LAN_sentences)
        # Saving to file
        print "Pickling the corpus"
        
        # Writing JSON data
        with open(filename, 'w') as f:
             ujson.dump(LAN_sentences, f)
        f.close()
    return LAN_sentences    

# In[141]:

"""
#Implement Code Switching here 

def ACS_sentences(ENG_sentences):
    for line in ENG_sentences:
        res=[]
        for word in line:
            x = acs(word)
            res.append(x)
        ENG_sentences[ENG_sentences.index(line)]=res 
    return ENG_sentences

#ENG_sentences = ACS_sentences(ENG_sentences)
"""
 
def multilingualcorpus(mode,LAN1_sentences,LAN2_sentences,filename):
    multilingual_data=[]
    if mode=="Save":
        
        # Assimilated Corpus of Multilingual texts        
        multilingual_data= LAN1_sentences + LAN2_sentences
        # Random shuffle of the sentences
        shuffle(multilingual_data)
        # Saving to file
        print "Pickling Multi-Corpus"
        
        # Writing JSON data
        with open(filename, 'w') as f:
             ujson.dump(multilingual_data, f)
        f.close()
	print "Corpus saved"
        
    if mode=="Load":
    # Reading data back
	print "Load Corpus"
        with open(filename, 'r') as f:
             multilingual_data = ujson.load(f)
        f.close()
        print "Done with Multi-Lingual Corpus"
    return multilingual_data


def embeddings(LAN_sentences,filename):
    """ 
    Using the word2vec implementation   
    - Initialize a model
    Parameters:
    - (sg=0), CBOW is used. Otherwise (sg=1), skip-gram is employed
    - size is the dimensionality of the feature vectors.
    - window is the maximum distance between the current and predicted word within a sentence.
    - min_count => ignore all words with total frequency lower than this.
    
    Taking the corpus in the required format or word2vec as LAN_sentences and saving it in a text file using filename
    """
    # Word2Vec
    print "Saving Language model"
    model_eng = models.Word2Vec(LAN_sentences, size=300, window=5, min_count=5, workers=4)
    model_eng.save(filename)
    print "Word2Vec embeddings complete"

    
def evaluate_embeddings(model,testfile):
    """
    Evaluating the Embeddings
    
    -Performing NLP word tasks with the model
    -Probability of a text under the model
    -Correlation with human opinion on word similarity and on analogies
    -Question-words: Google have released their testing set of about 20,000 syntactic and semantic test examples, 
    following the “A is to B as C is to D” task
    - Doesn't match
    - Most similar
    
    
    """
    print "Evaluating the Model"
    accudict= model.accuracy(testfile)
    
    for i in range(len(accudict)):
        print "For category ", accudict[i]['section'], "Accuracy is ", 100*float(len(accudict[i]['correct']))/(len(accudict[i]['incorrect'])+len(accudict[i]['correct']))
    
    
    
def corpus_stats(modelfile,testfile):
    print "------Corpus Statistics------"
    # Loading the models
    model_lan = gensim.models.Word2Vec.load(modelfile)
    vocab_lan = list(model_lan.wv.vocab.keys())
    print "\n Vocabulary length of Corpus : ", len(vocab_lan)
    print "Evaluating English embeddings "
    evaluate_embeddings(model_lan,testfile)


    
# Persist a model to disk
fname0 = os.path.join(os.getcwd(),'word_vectors_eng.txt')
fname_comp = os.path.join(os.getcwd(),'word_vectors_eng_compress.txt')

fname1 = os.path.join(os.getcwd(),'word_vectors_esp.txt')
fname2 = os.path.join(os.getcwd(),'word_vectors_fre.txt')
fname3 = os.path.join(os.getcwd(),'word_vectors_ita.txt')

fnamex1 = os.path.join(os.getcwd(),'wv_enes_mul.txt')
fnamex2 = os.path.join(os.getcwd(),'wv_enfr_mul.txt')
fnamex3 = os.path.join(os.getcwd(),'wv_enit_mul.txt')

fnameacs1 = os.path.join(os.getcwd(),'wv_enes_acs.txt')
fnameacs2 = os.path.join(os.getcwd(),'wv_enfr_acs.txt')
fnameacs3 = os.path.join(os.getcwd(),'wv_enit_acs.txt')

test_eng = os.path.join(os.getcwd(),'questions-words.txt')
test_esp = os.path.join(os.getcwd(),'questions-words_esp.txt')
test_ita = os.path.join(os.getcwd(),'questions-words_ita.txt')
        
"""
Uncomment the corresponding lines to process corpus or load data

"""        
#ESP_sentences = parsecorpus("Save",ESP_DIR,'espdata.json',5)
#ESP_sentences = parsecorpus("Load",ESP_DIR,'espdata.json',5)

#FRE_sentences = parsecorpus("Save",ESP_DIR,'fredata.json',5)
#FRE_sentences = parsecorpus("Load",ESP_DIR,'fredata.json',5)

#ITA_sentences = parsecorpus("Save",ESP_DIR,'itadata.json',5)
#ITA_sentences = parsecorpus("Load",ESP_DIR,'itadata.json',5)

#ENG_sentences = parsecorpus("Save",ENG_DIR,'engdata.json',5)
#ENG_sentences = parsecorpus("Load",ENG_DIR,'engdata.json',5)

#ENG_sentences = parsecorpus("Save",ENG_DIR,'engdata_compress.json',8)
#ENG_sentences = parsecorpus("Load",ENG_DIR,'engdata_compress.json',8)

"""
Uncomment the corresponding lines to merge corpus

""" 
#multilingual_data = multilingualcorpus("Save",ENG_sentences, ESP_sentences,'en_es.json')
#multilingual_data = multilingualcorpus("Load",[],[],'en_es.json')

#multilingual_data = multilingualcorpus("Save",ENG_sentences, FRE_sentences,'en_fr.json')
#multilingual_data = multilingualcorpus("Load",[],[],'en_fr.json')

#multilingual_data = multilingualcorpus("Save",ENG_sentences, ITA_sentences,'en_it.json')
#multilingual_data = multilingualcorpus("Load",[],[],'en_it.json')

"""
Uncomment the corresponding lines to generate embeddings

""" 

#embeddings(ENG_sentences,fname0)
#embeddings(ENG_sentences,fname_comp)
#embeddings(ESP_sentences,fname1)
#embeddings(FRE_sentences,fname2)
#embeddings(ITA_sentences,fname3)


#embeddings(multilingual_data,fnamex1)
#embeddings(multilingual_data,fnamex2)
#embeddings(multilingual_data,fnamex3)

#embeddings(multilingual_data,fnameacs1)
#embeddings(multilingual_data,fnameacs2)
#embeddings(multilingual_data,fnameacs3)


"""
Uncomment the corresponding lines to print corpus statistics

""" 

#corpus_stats(fname0,test_eng)
#corpus_stats(fname_comp,test_eng)

#corpus_stats(fname1,test_esp)
#corpus_stats(fnamex1,test_esp)
#corpus_stats(fnameacs1,test_esp)

#corpus_stats(fname3,test_ita)
#corpus_stats(fnamex3,test_ita)
#corpus_stats(fnameacs3,test_ita)




