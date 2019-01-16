import argparse
import os
from nltk.stem import PorterStemmer
path=os.getcwd()
pathForwardIndex=path+"\\doc_index.txt";
pathTerminfo=path+"\\term_info.txt";
pathDocId=path+"\\docids.txt"
pathtid=path+"\\termids.txt"
pathinverted=path+"\\term_index.txt"
parser = argparse.ArgumentParser(description='Query Index Information')
parser.add_argument("--doc", type=str,
	help="name of the document")
parser.add_argument("--term", type=str,
	help="the term")

args = vars(parser.parse_args())


def preprocessing(token):   # this function make tokens , convert to lower case, and stem them
    
    token = token.lower();
    ps = PorterStemmer(); 
    token = ps.stem(token);
    return token;


#query of form --doc -- term
def BothGiven(term, doc):
    print("Inverted list for term : ",term)
    print("In document :", doc)
    term = preprocessing(term)
    with open(pathtid) as f:
        lines = f.readlines()
        termid=0
        for item in lines:
            splited = item.split('\t')
            term_name = splited[1].split('\n')
            if term_name[0] == term:
                termid = splited[0]
        if termid == 0:
            print(       "Error!!! Term not found!!!!")
            exit()
	
    with open(pathDocId) as f:
        lines = f.readlines()
        docid = 0
        for item in lines:
            splited = item.split('\t')  # print(splited)
            docname = splited[1].split('\n')

            if docname[0] == doc:
                docid = splited[0]
        if docid == 0:
            print(       "Error!!! Document not found!!!!")
            exit()
		
    with open(pathinverted) as f2:
	   
        lines2=f2.readlines()
        for item in lines2:
            spliteddata = item.split('\t')
            found = 0
            positions=[]
            if spliteddata[0]== termid:
                print("TERMID: "+ str(termid) +"\n")
                print("DOCID: "+ str(docid) +"\n")
                prevdoc=0
                prevpos=0
                for i in range(len(spliteddata)-2):
                    split = spliteddata[i+1].split(':')
                    if (int(prevdoc) + int(split[0])) == int(docid):
                        pos = split[1].split('\n')
                        prevpos = int(prevpos) + int(pos[0])
                        positions.append(str(prevpos))
                        found = 1

                    elif(found == 1):
                        break
                    prevdoc = int(prevdoc) + int(split[0])
            if(found == 1):
                break
        if(found == 0):
            print("term not found in given doc!!!")
        else:
            print('positions :',str(positions))

#query of form --doc
def docGiven(term, doc):
    
    term = preprocessing(term);
    with open(pathDocId) as f:
        lines = f.readlines()
    docid = 0
    for item in lines:
        splited = item.split('\t')  # print(splited)
        docname = splited[1].split('\n')

        if docname[0] == doc:
            docid = splited[0]
    if docid == 0:
        print(       "Error!!! Document not found!!!!")
        exit()
    with open(pathForwardIndex) as f2:
        lines2=f2.readlines()
        distinct = 0
        totalterms = 0
        for item in lines2:
            spliteddata = item.split('\t')
            if spliteddata[0] == docid:
                print(spliteddata)
                length = len(spliteddata) - 2
                distinct += 1
                totalterms+=length

        print("Listing for document : " + doc + '\n')
        print(   "DOCID : " + str(docid) + '\n')
        print("Distinct Terms : " + str(distinct) + '\n')
        print(    "Total Terms : " + str(totalterms) + '\n')


#query of form -- term
def termGiven(term, doc):
    term = preprocessing(term);
    with open(pathtid) as f:
        lines = f.readlines()
    termid = 0
    for item in lines:
        splited = item.split('\t')
        splited1 = splited[1].split('\n')
        if splited1[0] == term:
            termid = splited[0]
    if termid == 0:
        print(       "Error!!! Term not found!!!!")
        exit()
    with open(pathTerminfo) as f:
        lines = f.readlines()
    for item in lines:
        spliteddata = item.split('\t')
        if spliteddata[0] == termid:
            print(   "Listing for term : " + term + '\n')
            print(      "TERMID : " + str(termid) + '\n')
            print( "Total number of Documents Containing Terms : " + str(spliteddata[3]) + '\n')
            print(
            "No of Containing Terms : " + str(spliteddata[2]) + '\n')
            print(
            "Inverted List Offset : " + str(spliteddata[1]) + '\n')
            break



if args['doc']!=None:
    if args['term']!=None:
        BothGiven(format(args['term']),format(args['doc']))
    else:
        docGiven(format(args['term']), format(args['doc']))
else:
    termGiven(format(args['term']),format(args['doc']))
