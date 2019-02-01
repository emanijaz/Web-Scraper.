from __future__ import print_function
import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer

dirpath = os.getcwd()
corpus_path=dirpath+"\\corpus\\"


def document_parsing(doc):
    text = "";
    soup = BeautifulSoup(doc.read(), 'html.parser'); # parsing web document
    for script in soup(['script', 'style']): # remove all script and style codes  
        script.extract();
    for body in soup.find_all('body'):  # grap all content from body only and ignore header 
        text = body.get_text();
    return text;   # return parsed text
    
def preprocessing(text):   # this function make tokens , convert to lower case, and stem them

    print("\n  *****   TOKENIZING    *********\n")
    tokenizer = RegexpTokenizer('[a-zA-Z]+') # using reg exp to get words as token
    tokenized_text = tokenizer.tokenize(text) # returns all tokens
    print("\n  *****   LOWER CASING **** REMOVING STOP WORDS    *********\n")
    tokenized_text = [token.lower() for token in tokenized_text if token.lower() not in stop_words]; # converting to lower case and removing stop words
    print("\n  *****   STEMMING    *********\n")
    ps = PorterStemmer(); 
    tokenized_text = [ps.stem(token) for token in tokenized_text]; # applying stemming
    return tokenized_text;

def preprocessingWithoutStopWords(text):
    tokenizer = RegexpTokenizer('[a-zA-Z]+')
    tokenized_text = tokenizer.tokenize(text)
    tokenized_text = [token.lower() for token in tokenized_text]
    ps = PorterStemmer()
    tokenized_text = [ps.stem(token) for token in tokenized_text]
    return tokenized_text
    
    
def file_docids(docID, doc_name):
    docID_file.write(str(docID)); ## writing doc with ID's
    docID_file.write("\t");
    docID_file.write(doc_name);
    docID_file.write("\n");
    


def file_termids(terms):
    termID_file = open(dirpath+"\\termids.txt","w");
    for t in terms:
        termID_file.write(str(terms.index(t)+1)); # write term ID
        termID_file.write("\t");
        termID_file.write(t); ## write term 
        termID_file.write("\n");
    termID_file.close();

def file_doc_index(docID, terms, tokenized_text_duplicates,tokenized_text):
    
    for tok in tokenized_text: 
        position = [pos for pos,word in enumerate(tokenized_text_duplicates) if word == tok];# finding positions 
        doc_index_file.write(str(docID));  # write document ids
        doc_index_file.write("\t");
        doc_index_file.write(str(terms.index(tok)+1));  # writing termID after getting index of that term from terms list
        for p in position: # writing positions of term in file
            doc_index_file.write("\t");
            doc_index_file.write(str(p+1));
        doc_index_file.write("\n");
    



stop_words_file = open(dirpath+"\\stoplist.txt","r");
stop_words  = stop_words_file.read();
docID = 1;          ## indexer for doc files
terms = [];            ## a list containing all terms from all files
docID_file = open(dirpath+"\\docids.txt","w");
doc_index_file = open(dirpath+"\\doc_index.txt","w")

################# DON'T    FORGET   TO CHANGE   PATH   OF    CORPUS    DIRECTORY  !!!!!!!!!!!!!!" 
files = os.listdir(corpus_path)     # files from corpus

for doc_name in files:   ## loop on all docs in corpus
    
    print("*****************    processing document ", docID, " *******************");

################# DON'T    FORGET   TO CHANGE   PATH   OF    CORPUS    DIRECTORY  !!!!!!!!!!!!!!" 
	
    path = corpus_path; 
    path = path  +doc_name;
    doc = open(path,"r", encoding="utf8", errors='ignore');
    
    text = document_parsing(doc);          # calling function for doc parsing
    if text == "":
        print("no text existed .... DOC is empty !!!! ");
        continue;
    tokenized_text = preprocessing(text);
   
    tokenized_text_duplicates = tokenized_text;
   # removing duplicates , making unique set
    tokenSet =[]
    for item in tokenized_text:
        if item not in tokenSet:
            tokenSet.append(item);
    tokenized_text = tokenSet;
	temp = set(tokenSet)
	# for idx, item in enumerate(temp):
    for token in tokenized_text:
        if token not in terms:  ## if token doesn't exist already
            terms.append(token);  ## appending all tokens of current doc in terms list

    file_doc_index(docID, terms, preprocessingWithoutStopWords(text),tokenized_text) # writing to doc_index file
    file_docids(docID, doc_name); # writing to file docids
    docID = docID + 1;  ## incrementing doc ID 

file_termids(terms); # writing to termids file

docID_file.close(); 
doc_index_file.close()



