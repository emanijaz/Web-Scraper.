import os
#file Reading
import itertools
from collections import defaultdict

import re



def makeIndexBSBI():
    def takeSecond(elem):
        return elem[1]
    def takeFirst(elem):
        return elem[0]
    dirpath = os.getcwd()
    filepath=dirpath+"\\doc_index.txt"
    with open (filepath) as f:
        forwardIndex=f.readlines();

    termIndex=open(dirpath+'\\term_index.txt','w+')
    term_info=open(dirpath+'\\term_info.txt','w+')
    stuff=[]
    for item in forwardIndex:
        x=list(item.split('\t'))
        x.pop(len(x) - 1)
        stuff.append(x)
    stuff=sorted(stuff,key=takeSecond)
    postings=[]
    terms=[]
    #for each term we group its documents
    #k=term
    for k, g in itertools.groupby(stuff,key=takeSecond):
        g=sorted(g,key=takeFirst)

        postings.append(list(g))  # Store group iterator as a list
        Noofdoc=len(list(g))
        termIndex.write(str(k) + '\t')
        prevdocId=0;#for delta encoding we need pre doc id number
        freqIncorpus=0
        term_info.write(str(k)+'\t')
        term_info.write(str(termIndex.tell()) + '\t')#offset of present term stored as meta data
        for doc in list(g):
            docid=int(doc[0])-prevdocId#delta encoded
            prevdocId=int(doc[0])
            freqInthedoc=len(doc)-2;#we cut out one for docId and one for term id doc is of form ['docid', 'term', 'position2592', '2973']
            freqIncorpus+=freqInthedoc

            #for each document we write the position where term occured
            for i in range(0,freqInthedoc):
                if(i==0):                          #doc[i+2] gives position
                    termIndex.write(str(docid)+":"+str(doc[i+2]) + '\t')
                else:
                    termIndex.write("0"+ ":" + str(doc[i + 2]) + '\t')
        termIndex.write('\n')
        term_info.write(str(freqIncorpus) + '\t'+ str(Noofdoc)+'\n')
    termIndex.close()
    term_info.close()

def makeIndexSPIMI():
    def takeSecond(elem):
        return elem[1]
    def takeFirst(elem):
        return elem[0]
    dirpath = os.getcwd()
    filepath=dirpath+"\\doc_index.txt"
    with open (filepath) as f:
        forwardIndex=f.readlines();

    termIndex=open(dirpath+'\\term_index.txt','w+')
    term_info=open(dirpath+'\\term_info.txt','w+')
    indexHashMap=defaultdict(list)
    for item in forwardIndex:
        x=list(re.split("\t|\n",item))
        x.pop(len(x)-1)
        freqIndoc=len(x)-2;
        #print("frq0"+str(freqIndoc))
        term=str(x[1])
        doc=x[0]
        prevPos=0

        postings=[]
        if term in indexHashMap:
            postings=indexHashMap.get(term)
            #print("docPrev"+str(postings[0]))
            for i in range(0,freqIndoc):
                if(i==0):
                    prevDocId=postings[0]
                    prevPos=x[i+2]
                    delta=int(doc)-int(prevDocId)
                    indexHashMap[term].append(str(delta)+":"+str(x[i+2]))
                else:
                    PositiondeltaCode=int(x[i+2])-int(prevPos)
                    indexHashMap[term].append("0:" + str(PositiondeltaCode))
                    prevPos=x[i+2]

        else:

            for i in range(0, freqIndoc):
                if (i == 0):

                    indexHashMap[term].append(str(doc))#prevDocId
                    prevPos = x[i + 2]
                    indexHashMap[term].append(str(doc) + ":" + str(x[i + 2]))

                else:
                    PositiondeltaCode = int(x[i + 2]) -int(prevPos)
                    indexHashMap[term].append("0:" + str(PositiondeltaCode))
                    prevPos = x[i + 2]
                    #print(indexHashMap[term])
        indexHashMap[term][0]=str(doc)

    for terms in indexHashMap:
        termIndex.write(str(terms)+"\t")
        term_info.write(str(terms) + "\t")
        term_info.write(str(termIndex.tell())+"\t")
        i=0;#oignore the first posting its prev docid
        Totaldocs=0;
        for postings in indexHashMap[terms]:
            if(i!=0):
                termIndex.write(str(postings)+"\t");
                temp=postings.split(":")
                if temp[0] != "0":
                    Totaldocs=Totaldocs+1
            else:
                i=1;

        totfreq= len(indexHashMap[terms])-1
        term_info.write(str(totfreq) + "\t")
        term_info.write(str(Totaldocs) + "\n")
        termIndex.write("\n")

    termIndex.close()
    term_info.close()
    print(indexHashMap["aspargu"])


makeIndexSPIMI()
