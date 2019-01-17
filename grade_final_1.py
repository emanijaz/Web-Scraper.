from __future__ import print_function
import argparse
import numpy as np
import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from nested_dict import nested_dict
from nltk.tokenize import sent_tokenize,word_tokenize
import re
import math
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
import collections

D=3446
avgDocumenLenght=1148
totalQueries=10
dirpath = os.getcwd()
def query_avg_len(queries):
    total_terms = 0
    for query in queries:
        separated_query = preprocessing(queries[query])
        total_terms += len(separated_query)
    return total_terms / len(queries)

#parser = argparse.ArgumentParser(description='Query Index Information')
#parser.add_argument("--score", type=str,
#	help="scoring function name")
#args = vars(parser.parse_args())

path=os.getcwd()
pathForwardIndex=path+"\\doc_index.txt";
pathTerminfo=path+"\\term_info.txt";
pathDocId=path+"\\docids.txt"
pathtid=path+"\\termids.txt"
pathinverted=path+"\\term_index.txt"
corpus_path=dirpath+"\\corpus\corpus\\"
files = os.listdir(corpus_path)
parser = argparse.ArgumentParser(description='Query Search Engine')
parser.add_argument("--score", type=str,
	help="ranked retrieval using the score")

args = vars(parser.parse_args())

stop_words_file = open(dirpath+"\\stoplist.txt","r")
stop_words = stop_words_file.read()

##############################Proocess the topics.xml to get the queres######################################
def GetQueries(queryFilename):
    queries = {}
    with open(queryFilename) as F:
        xml_soup = BeautifulSoup(F.read(),'lxml')
        for topic in xml_soup.find_all('topic'):
            queries[topic['number']]= topic.query.string
    return queries
#--------------------#

text = GetQueries(dirpath + "//topics.xml")

def doc_parsing(doc):
    text = "";
    soup = BeautifulSoup(doc.read(), 'html.parser');  # parsing web document
    for script in soup(['script', 'style']):  # remove all script and style codes
        script.extract();
    for body in soup.find_all('body'):  # grap all content from body only and ignore header
        text = body.get_text();
    return text;  # return parsed text

def query_parsing(doc):
    text = []
    soup = BeautifulSoup(doc, 'html.parser')
    for script in soup('description'):
        script.extract()
    for query in soup.find_all('query'):
         text.append(query.get_text())
    return text   # return parsed text

def preprocessing(text):   # this function make tokens , convert to lower case, and stem them

    tokenizer = RegexpTokenizer('[a-zA-Z]+')  # using reg exp to get words as token
    tokenized_text = tokenizer.tokenize(text)  # returns all tokens
    tokenized_text = [token.lower() for token in tokenized_text if token.lower() not in stop_words] # converting to lower case and removing stop words
    ps = PorterStemmer()
    tokenized_text = [ps.stem(token) for token in tokenized_text] # applying stemming
    return tokenized_text

def square(list):
    return [i ** 2 for i in list]

def takeFirst(elem):
    return elem[0]

def get_termID_dict():  ## return dict with format  term name : term id
    term_id_list = {}
    with open(pathtid) as f:
        lines = f.readlines()
        termid = 1
        for item in lines:
            splited = item.split('\t')
            term_name = splited[1].split('\n')
            # print("term name is : ", term_name[0])
            term_id_list[term_name[0]] = termid
            termid += 1

        return term_id_list

def queries_info():  # return dictionary with format  { termid : [[docid, freq in doc, ctf], ....... for all 3446 docs ] }

    dict = {}
    termID_dict = get_termID_dict()
    with open(pathinverted) as f2:
        lines = f2.readlines()
    for query in text:
        tokenized_query = preprocessing(text[query])
        for term in tokenized_query:
            dict[termID_dict[term]] = list()
            for i in range(0, 3446):
                dict[termID_dict[term]].append([i + 1, 0, 0])  # would have docid, term freq in doc, ctf

    for item in lines:
        spliteddata = item.split('\t')
        if int(spliteddata[0]) in dict:
            termid = int(spliteddata[0])
            ctf = len(spliteddata) - 2  # exclude termID rest length is
            for j in range(0, 3446):
                dict[termid][j][2] = ctf
            prevdoc = 0
            for i in range(len(spliteddata) - 2):
                split = spliteddata[i + 1].split(':')
                dict[termid][prevdoc + int(split[0]) - 1][1] += 1  # increase term freq
                prevdoc = int(prevdoc) + int(split[0])

    return dict

def DocumentLenghts():
    with open(pathForwardIndex) as f2:
        lines2 = f2.readlines()
    doclneghts={}
    distinct = 0
    totalterms = 0
    for item in lines2:
        spliteddata = item.split('\t')
        if int(spliteddata[0]) in doclneghts:
            doclneghts[int(spliteddata[0])]+=len(spliteddata) - 2
        else:
            doclneghts[int(spliteddata[0])] = len(spliteddata) - 2

    return doclneghts

def doc_avg_len():  # average document length
    total_terms = 0
    with open(pathForwardIndex) as f2:
        lines2 = f2.readlines()
        for item in lines2:
            spliteddata = item.split('\t')
            total_terms += len(spliteddata) - 2
    return total_terms / len(files)

def documents_containing_terms(): ## return dict with format  {termid: total number of docs containning that term}
    docs_count_dict = {}
    with open(pathTerminfo) as f2:
        lines = f2.readlines()
    for item in lines:
        split = item.split('\t')
        totalDocHavingTerm = split[3].split('\n')[0]
        termid = split[0]
        docs_count_dict[int(termid)] = int(totalDocHavingTerm)
    return docs_count_dict

def queries_containing_terms():  ## return dict with format  {term: total number of queries containning that term}
    queries_count_dict ={}
    qterms = []
    for query in text:
        tokenized_query = preprocessing(text[query])
        for term in tokenized_query:
            if term not in qterms:
                qterms.append(term)
                queries_count_dict[term] = 0
    for term in qterms:
        for query1 in text:
            tokenized_query1 = preprocessing(text[query1])
            if term in tokenized_query1:
                queries_count_dict[term] += 1
    return queries_count_dict

def takeSecond(elem):
    return elem[1]

def DocsInfo_BM25():
    total_length = 0
    doc_length_dict = {}
    with open(pathDocId) as f:
        lines = f.readlines()
    docs={}
    for line in lines:
        doc_name = line.split('\t')
        # if(doc_name[0]==1373):
        #     print("herre")
        #print(doc_name[0])
        docs[int(doc_name[0])] = doc_name[1].split('\n')[0]

    return docs

def DocsInfo():  # returns sum of lengths of all docs in corpus and dict with format  docID :[docname, doclength]
    total_length = 0
    doc_length_dict = {}
    with open(pathDocId) as f:
        lines = f.readlines()
    for i in range(0, 3446):
        doc_name = lines[i].split('\t')
        doc_name = doc_name[1].split('\n')
        # doc_length_dict[i+1] = [lines[i].split('\t')[1], 0]
        doc_length_dict[i + 1] = [doc_name[0], 0]

    with open(pathForwardIndex) as f2:
        lines2 = f2.readlines();
        for item in lines2:
            spliteddata = item.split('\t')
            doc_length_dict[int(spliteddata[0])][1] = doc_length_dict[int(spliteddata[0])][1] + len(spliteddata) - 2
            total_length += len(spliteddata) - 2
        return total_length, doc_length_dict;


termid_dict = get_termID_dict()
 ########### functions for  TF #####3
def dict_oktf_query(): ## return dict with query number as key and its oktf list as value
    dict = {}
    for  k in range(0,10):
        dict[k+1] = []
    i = 1
    for query in text:
        tokenized_query = preprocessing(text[query])
        oktf_query = []
        for term in tokenized_query:  # oktf for each term in query
            term_freq_in_query = tokenized_query.count(term)
            oktf_q = term_freq_in_query / (term_freq_in_query + 0.5 + (1.5 * len(tokenized_query) / query_avg_len(text)))
            oktf_query.append(oktf_q)

        dict[i] = oktf_query
        i = i+1
    return dict
def dict_oktf_doc():  ## dict with query no as key and 3446 numbers of list with oktf of each doc
    term_dict = get_termID_dict()
    dict2 = queries_info()
    l, docs_dict = DocsInfo()
    q_avg_l = query_avg_len(text)
    dict = {}
    for k in range(0,10):
        dict[k+1] = list(range(0,3446))
    i = 1
    for query in text:
        tokenized_query = preprocessing(text[query])

        for j in range(0,3446):
            oktf_doc = []
            for term in tokenized_query:  # oktf for each term of query found in doc
                if term in term_dict:
                    term_freq_in_doc = dict2[term_dict[term]][j][1]
                else:
                    term_freq_in_doc = 0
                oktf_d = term_freq_in_doc / (term_freq_in_doc + 0.5 + (1.5 * docs_dict[j+1][1]/ q_avg_l))
                oktf_doc.append(oktf_d)
            dict[i][j] = oktf_doc
        i=i+1
    return dict

no_of_docs = documents_containing_terms()
no_of_queries = queries_containing_terms()

########### functions for  TF_IDF #####3
def TFIDF_dict_oktf_query():
    dict = {}
    for k in range(0, 10):
        dict[k + 1] = []
    i = 1
    for query in text:
        tokenized_query = preprocessing(text[query])
        oktf_query = []
        for term in tokenized_query:  # oktf for each term in query
            term_freq_in_query = tokenized_query.count(term)
            oktf_q = term_freq_in_query / (
                        term_freq_in_query + 0.5 + (1.5 * len(tokenized_query) / query_avg_len(text)))
            oktf_query.append(oktf_q * math.log10(10 / no_of_queries[term]))

        dict[i] = oktf_query
        i = i + 1
    return dict
def TFIDF_dict_oktf_doc():


    term_dict = get_termID_dict()
    dict2 = queries_info()
    l, docs_dict = DocsInfo()
    q_avg_l = query_avg_len(text)
    dict = {}
    for k in range(0, 10):
        dict[k + 1] = list(range(0, 3446))
    i = 1
    for query in text:
        tokenized_query = preprocessing(text[query])

        for j in range(0, 3446):
            oktf_doc = []
            for term in tokenized_query:  # oktf for each term of query found in doc
                if term in term_dict:
                    term_freq_in_doc = dict2[term_dict[term]][j][1]
                else:
                    term_freq_in_doc = 0
                oktf_d = term_freq_in_doc / (term_freq_in_doc + 0.5 + (1.5 * docs_dict[j + 1][1] / q_avg_l))
                oktf_doc.append(oktf_d * math.log10(3446 / no_of_docs[termid_dict[term]]))
            dict[i][j] = oktf_doc
        i = i + 1
    return dict


########################### functions ###########

def TF():
    okapi_tf = open(dirpath + '\\TF.txt', 'w')
    avg_doc_length = doc_avg_len()
    all_query_score = []
    l, docs_dict = DocsInfo()

    oktf_doc= dict_oktf_doc()
    oktf_query = dict_oktf_query()

    oktf_doc1_dict = {}
    for j in range(0,3446):
        oktf_doc1_dict[j+1]=[]

    with open(pathForwardIndex) as f2:
        lines = f2.readlines()
    for item in lines:
        splittedata = item.split('\t')
        term_freq_in_doc = len(splittedata) - 2
        oktf_d1 = term_freq_in_doc / (term_freq_in_doc + 0.5 + (1.5 * docs_dict[int(splittedata[0])][1] / avg_doc_length))
        oktf_doc1_dict[int(splittedata[0])].append(oktf_d1)

    q=1
    for query in text:
        score = 0
        doc_score = []
        for doc in range(0,3446):
            doc_name = docs_dict[doc+1][0]
            if (math.sqrt(sum(square(oktf_doc1_dict[doc+1]))) * math.sqrt(sum(square(oktf_query[q])))) != 0:
                score = sum([a * b for a, b in zip(oktf_doc[q][doc], oktf_query[q])]) / (
                            math.sqrt(sum(square(oktf_doc1_dict[doc+1]))) * math.sqrt(sum(square(oktf_query[q]))))
            doc_score.append((score, doc_name))
        sortedlist = sorted(doc_score, key=takeFirst, reverse=True)
        rank = 1
        for score in sortedlist:
            okapi_tf.write(query + " 0 " + str(score[1]) + " " + str(rank) + " " + str(score[0]) + " run1 " + "\n")
            rank += 1

        print("query done")
        all_query_score.append(doc_score)
        q=q+1
    okapi_tf.close()

def TF_IDF():
    okapi_tfidf = open(dirpath + '\\TF_IDF.txt', 'w')
    avg_doc_length = doc_avg_len()
    all_query_score = []
    l, docs_dict = DocsInfo()
    oktf_doc = TFIDF_dict_oktf_doc()
    oktf_query = TFIDF_dict_oktf_query()

    oktf_doc1_dict = {}
    for j in range(0, 3446):
        oktf_doc1_dict[j + 1] = []

    with open(pathForwardIndex) as f2:
        lines = f2.readlines()
    for item in lines:
        splittedata = item.split('\t')
        term_freq_in_doc = len(splittedata) - 2
        oktf_d1 = term_freq_in_doc / (
                    term_freq_in_doc + 0.5 + (1.5 * docs_dict[int(splittedata[0])][1] / avg_doc_length))
        oktf_doc1_dict[int(splittedata[0])].append(oktf_d1 * math.log10(3446 / no_of_docs[int(splittedata[0])]))

    q = 1
    for query in text:
        score = 0
        doc_score = []
        for doc in range(0, 3446):
            doc_name = docs_dict[doc + 1][0]
            if (math.sqrt(sum(square(oktf_doc1_dict[doc + 1]))) * math.sqrt(sum(square(oktf_query[q])))) != 0:
                score = sum([a * b for a, b in zip(oktf_doc[q][doc], oktf_query[q])]) / (
                        math.sqrt(sum(square(oktf_doc1_dict[doc + 1]))) * math.sqrt(sum(square(oktf_query[q]))))
            doc_score.append((score, doc_name))
        sortedlist = sorted(doc_score, key=takeFirst, reverse=True)
        rank = 1
        for score in sortedlist:
            okapi_tfidf.write(query + " 0 " + str(score[1]) + " " + str(rank) + " " + str(score[0]) + " run1 " + "\n")
            rank += 1

        print("query done")
        all_query_score.append(doc_score)
        q = q + 1
    okapi_tfidf.close()

def BM25(b,k1,k2):
    queries = GetQueries(dirpath + "//topics.xml")
    doclengts= DocumentLenghts()
    outputfile = open("BM25.txt", "w")
    avergaeQueryLengh=query_avg_len(queries)
    documentFrequency = {}
    offsets={}
    term_termid={}
    docsThatHasTerm=collections.defaultdict(list)
    TermFreq = nested_dict(2, int)
    terms=[]
    for query in queries:
        tokenised = preprocessing(queries[query])
        terms.extend(tokenised)
    terms=set(terms)
    with open(pathtid) as file:
        termidssLayLo = file.readlines();
    for item in termidssLayLo:
        hell=item.split("\t")[1].split("\n")[0]
        if hell in terms:
            term_termid[hell] = item.split("\t")[0]
    with open(pathTerminfo) as myterms:
        termsInfor = myterms.readlines()

    for lines in termsInfor:
            terminformation = lines.split("\t")
            if terminformation[0] in term_termid.values():
                offsets[terminformation[0]] = terminformation[1]
                documentFrequency[terminformation[0]] = int(terminformation[3].split("\n")[0])
    with open(pathinverted) as invertedindex:
        for offset in offsets:
            invertedindex.seek(int(offsets[offset]))
            BusKardoTerm = invertedindex.readline()
            # print(BusKardoTerm)
            BusKardoTerm = BusKardoTerm.split("\t")
            documentid = int(BusKardoTerm[0].split(':')[0])
            for i in range(0, len(BusKardoTerm) - 1):
                moresplit = BusKardoTerm[i].split(':')
                if moresplit[0] != '0':
                    # print( moresplit[0])
                    if i != 0:
                        documentid = int(documentid) + int(moresplit[0])
                        docsThatHasTerm[offset].append(documentid)
                        TermFreq[offset][documentid] = 1
                        freq = 0;
                else:
                    TermFreq[offset][documentid] += 1;




    print(TermFreq)
    print(documentFrequency)
    for query in queries:
        JoDocumentsTermKa=[]
        tokenised=preprocessing(queries[query])
        for term in tokenised:
            JoDocumentsTermKa.extend(docsThatHasTerm[term_termid[term]])
        print(JoDocumentsTermKa)
        JoDocumentsTermKa = set(JoDocumentsTermKa)
        oktf_query = []
        print("the documents")
        print(JoDocumentsTermKa)
        MereSirKDard = []

        for item in JoDocumentsTermKa:
            lenght=doclengts[item]
            docvectore = []
            score=0;
            K = k1 * ((1 - b) + (b * lenght / avgDocumenLenght))
            for item1 in tokenised:
                docfre=float(documentFrequency[term_termid[item1]])-1
                A=np.log10((D + .5) / (docfre + 0.5))
                B=((1 + k1) * TermFreq[term_termid[item1]][item]) / (K + TermFreq[term_termid[item1]][item])
                C=float((( 1 + k2) * tokenised.count(item1)) / (k2 + tokenised.count(item1)))
                temp = (A * B * C)
                score+=temp
            MereSirKDard.append((item,score))
        docs=DocsInfo_BM25()

        MereSirKDard = sorted(MereSirKDard, key=takeSecond,reverse=True)
        print("the meresirkdard")
        print(MereSirKDard)
        lengthakhri = len(MereSirKDard)
        for j in range(0, lengthakhri):
            outputfile.write(query)
            outputfile.write("  0 ")
            outputfile.write(str(docs[MereSirKDard[j][0]]))
            outputfile.write(' ' + str(j + 1) + ' ')
            outputfile.write(' ' + str(MereSirKDard[j][1]) + ' ')
            outputfile.write("run1\n")
        print("done with query "+str(query)+"\n")
    outputfile.close()

def JM(): # Jelinek Mercer

    text = GetQueries(dirpath + "//topics.xml")
    JM_file = open(dirpath + '\\JM_lambda0.6.txt', 'w')
    lamda = 0.6
    all_query_score = []
    all_docs_length, doc_length_dict = DocsInfo() # return length of all documents and dict having keys as doc and values as thier length
    termID_dict = get_termID_dict()
    dict1 = queries_info()
    for query in text:
        doc_score = []
        tokenized_query = preprocessing(text[query])


        for doc in range(0,3446):
            term_prob = 1
            for term in tokenized_query:
                term_freq_in_doc = dict1[termID_dict[term]][doc][1]
                cummulative_term_freq = dict1[termID_dict[term]][doc][2]
                doc_length = doc_length_dict[doc+1][1]
                if doc_length == 0:
                    term_prob = term_prob * ((1 - lamda) * (cummulative_term_freq / all_docs_length)) # avoid divsion by zero due to 0 doc_length
                else:
                    term_prob = term_prob * ((lamda * (term_freq_in_doc / doc_length)) + (
                            (1 - lamda) * (cummulative_term_freq / all_docs_length)))
            doc_score.append((term_prob, doc_length_dict[doc+1][0])) # appending probability and doc name

        sortedlist = sorted(doc_score, key=takeFirst, reverse=True)
        rank = 1
        for score in sortedlist:
            JM_file.write(query + " 0 " + str(score[1]) + " " + str(rank) + " " + str(score[0]) + " run4 " + "\n")
            rank += 1
        print("query done")
        all_query_score.append(doc_score)
    JM_file.close()

def JM_new():  ## ctf from inverted index
    queries = GetQueries(dirpath + "//topics.xml")
    doclengts= DocumentLenghts()
    avergaeQueryLengh=query_avg_len(queries)
    documentFrequency = {}
    offsets={}
    term_termid={}
    docsThatHasTerm=collections.defaultdict(list)
    TermFreq = nested_dict(2, int)
    terms=[]
    for query in queries:
        tokenised = preprocessing(queries[query])
        terms.extend(tokenised)
    terms=set(terms)
    with open(pathtid) as file:
        termidssLayLo = file.readlines();
    for item in termidssLayLo:
        hell=item.split("\t")[1].split("\n")[0]
        if hell in terms:
            term_termid[hell] = item.split("\t")[0]
    with open(pathTerminfo) as myterms:
        termsInfor = myterms.readlines()

    for lines in termsInfor:
            terminformation = lines.split("\t")
            if terminformation[0] in term_termid.values():
                offsets[terminformation[0]] = terminformation[1]
                documentFrequency[terminformation[0]] = int(terminformation[2])
    with open(pathinverted) as invertedindex:
        for offset in offsets:
            invertedindex.seek(int(offsets[offset]))
            BusKardoTerm = invertedindex.readline()
            # print(BusKardoTerm)
            BusKardoTerm = BusKardoTerm.split("\t")
            documentid = int(BusKardoTerm[0].split(':')[0])
            for i in range(0, len(BusKardoTerm) - 1):
                moresplit = BusKardoTerm[i].split(':')
                if moresplit[0] != '0':
                    # print( moresplit[0])
                    if i != 0:
                        documentid = int(documentid) + int(moresplit[0])
                        docsThatHasTerm[offset].append(documentid)
                        TermFreq[offset][documentid] = 1
                        freq = 0;
                    else:
                        TermFreq[offset][documentid] += 1;
    lamda = 0.6
    all_docs_length=0
    for doc in doclengts:
        all_docs_length+=doclengts[doc]
    docsm=DocsInfo_BM25()
    JM_file=open("JM_new.txt","w")
    for query in text:
        doc_score = []
        tokenized_query = preprocessing(text[query])

        for doc in range(1, D+1):
            term_prob = 1
            for term in tokenized_query:
                if doc in TermFreq[term_termid[term]]:
                    term_freq_in_doc = TermFreq[term_termid[term]][doc]
                else:
                    term_freq_in_doc = 0
                cummulative_term_freq = int(documentFrequency[term_termid[term]])
                if doc in doclengts:
                    doc_length = doclengts[doc]
                else:
                    doc_length=0
                if doc_length == 0:
                    term_prob = term_prob * ((1 - lamda) * (
                                cummulative_term_freq / all_docs_length))  # avoid divsion by zero due to 0 doc_length
                else:
                    term_prob = term_prob * ((lamda * (term_freq_in_doc / doc_length)) + (
                            (1 - lamda) * (cummulative_term_freq / all_docs_length)))

            doc_score.append((docsm[doc],term_prob))  # appending probability and doc name

        sortedlist = sorted(doc_score, key=takeSecond, reverse=True)
        print(sortedlist)
        rank = 1
        for score in sortedlist:
            JM_file.write(query + " 0 " + str(score[0]) + " " + str(rank) + " " + str(score[1]) + " run4 " + "\n")
            rank += 1
        print("query done")

    JM_file.close()

if __name__ == '__main__':



    parser = argparse.ArgumentParser(description='Query Search Engine')
    parser.add_argument("--score", type=str,
                        help="ranked retrieval using the score")

    args = vars(parser.parse_args())

    if args['score'] != None:
        if args['score'] == "TF_IDF":
            TF_IDF()
        elif args['score'] == "TF":
            TF()
        elif args['score'] == "BM25":
            BM25(.75, 1.2, 100)
        elif args["score"] == "JM":
            JM()
        elif args["score"] == "JM_new":
            JM_new()


