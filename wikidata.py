import os
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import argparse


DATA_DIR = "E:\GIT_ROOT\wikipedia_data"


TEST_DIR = "E:\GIT_ROOT\wikipedia_data\Test"
ENG_DIR = "E:\GIT_ROOT\wikipedia_data\English_Wiki"
FRE_DIR = "E:\GIT_ROOT\wikipedia_data\French_Wiki"
RUS_DIR = "E:\GIT_ROOT\wikipedia_data\Russian_Wiki"

ENG_PATH = "E:\GIT_ROOT\wikipedia_data\en"
FRE_PATH = "E:\GIT_ROOT\wikipedia_data\\fr"
RUS_PATH = "E:\GIT_ROOT\wikipedia_data\\rs"

ENG_TOKEN = "E:\GIT_ROOT\wikipedia_data\en_tokenized"
FRE_TOKEN = "E:\GIT_ROOT\wikipedia_data\\fr_tokenized"
RUS_TOKEN = "E:\GIT_ROOT\wikipedia_data\\rs_tokenized"




parser = argparse.ArgumentParser()
parser.add_argument("lang", help="Choose language",type=str)

args = parser.parse_args()


def parsecorpus():
    """
    Input parameters:

        2) DIR - Path to the corpus
        3) filename - 'abc.json', any name to pickle your corpus and save or load it.
                       Must be present in the same location, else change the code to find the file

    """
    if args.lang=="en":
        DIR=ENG_DIR
        PATH=ENG_PATH
        TOK=ENG_TOKEN
    elif args.lang == "fr":
        DIR = FRE_DIR
        PATH = FRE_PATH
        TOK = FRE_TOKEN
    else :
        DIR=RUS_DIR
        PATH=RUS_PATH
        TOK = RUS_TOKEN

    print("Starting....")
    print(DIR)
    for subdir, dirs, files in os.walk(DIR):
        with open(os.path.join(PATH,str(subdir)[-2:]), mode='w', encoding='utf-8') as f:
            for file in files:
                with open(os.path.join(subdir, file), mode='r', encoding='utf-8') as doc:
                    content = doc.read()
                    soup = BeautifulSoup(content, 'html.parser')
                    data = soup.get_text().lower()
                    s = sent_tokenize(data)
                    for line in s:
                        f.write(line)
                        f.write("\n")
            print("Done with: ",str(subdir)[-2:])
        f.close()




def map_wiki():
  """Maps a whole directory of .story files to a tokenized version using Stanford CoreNLP Tokenizer"""

  if args.lang == "en":
      DIR = ENG_DIR
      PATH = ENG_PATH
      TOK = ENG_TOKEN
      filename = "eng_mapping.txt"
  elif args.lang == "fr":
      DIR = FRE_DIR
      PATH = FRE_PATH
      TOK = FRE_TOKEN
      filename = "fre_mapping.txt"
  else:
      DIR = RUS_DIR
      PATH = RUS_PATH
      TOK = RUS_TOKEN
      filename="rus_mapping.txt"

  print("Preparing to tokenize %s to %s..." % (PATH, TOK))
  articles = os.listdir(PATH)
  # make IO list file
  print("Making list of files to tokenize...")
  with open(os.path.join(DATA_DIR,filename), "w") as f:
    for s in articles:
      f.write("%s \t %s\n" % (os.path.join(PATH, s), os.path.join(TOK, s)))
  f.close()

parsecorpus()
map_wiki()

# java -Xmx6g -XX:-UseGCOverheadLimit -cp /path_to_CoreNLP/classes:/path_to_CoreNLP/stanford-corenlp-models-current.jar
#  edu.stanford.nlp.process.PTBTokenizer -ioFileList -preserveLines eng_mapping.txt


def join_corpus():
    if args.lang == "en":
        DIR = ENG_DIR
        PATH = ENG_PATH
        TOK = ENG_TOKEN
        filename = "eng_mapping.txt"
        corpus="wikipedia_en"
    elif args.lang == "fr":
        DIR = FRE_DIR
        PATH = FRE_PATH
        TOK = FRE_TOKEN
        filename = "fre_mapping.txt"
        corpus = "wikipedia_fr"
    else:
        DIR = RUS_DIR
        PATH = RUS_PATH
        TOK = RUS_TOKEN
        filename = "rus_mapping.txt"
        corpus = "wikipedia_ru"

    articles = os.listdir(TOK)
    # make IO list file
    print("Combining all articles into one corpus file for % s in %s" %(args.lang,TOK))
    with open(os.path.join(DATA_DIR, corpus),mode="w",encoding="utf-8") as f:
        for s in articles:
            print("Copying :",s)
            with open(os.path.join(TOK, s), mode='r', encoding='utf-8') as doc:
                content = doc.read()
                soup = BeautifulSoup(content, 'html.parser')
                data = soup.get_text().replace("\n\n"," ")
                f.write(data)
        f.close()


join_corpus()
