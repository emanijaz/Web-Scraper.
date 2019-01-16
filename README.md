# Web-Scraper

## Summary:
A small search engine which provides ranks for given queries using TFIDF, IDF, Jelinek Mercer and Okapi BM25 scoring functions. 
It involves two parts:
  1. Inverted Index generation
  2. Ranker 
  
## INVERTED INDEX GENERATION:
Software reads websites data from given text files in corpus folder. It tokenizes the read data after preprocessing using several techniques. After preprocessing and tokenization it uses hashmaps to form inverted index of data. Furthermore, it ranks documents after reading inverted index and using Jelinek Mercer, BM25, TF, TFIDF scoring functions for provided queries. Queries are provided in topic.txt file.

## Files explanation:

Corpus folder contains .txt files with website data in all of them. 
**Tokenizer.txt**  provides code for reading web files from corpus and tokenizing them. It uses _Beautiful Soap_ python web scraping library, _Porter Stemmer_ technique and regex to preprocess the whole data. File **termids.txt** provides tokenized terms with ID's. **doc_index.txt** is forward index which lists the document ID's with all their corresponding terms and positions for each term in respective document.

Following is snippet of forward index:

![image](https://drive.google.com/uc?export=view&id=13KKVPM7yp99PSiPt83lZCisTVDGOr6ud)


## Termids.txt  
This file lists all terms found in all documents and assign ID’s to them. Following snippet clarifies the idea :

![image](https://drive.google.com/uc?export=view&id=1TD5ADt8TAHIRQOHyIbvOFniipqJoQ52W)

## Term_info.txt 
File that provides fast access time to the inverted list for any term in your index, and also provides extra metadata for the term. Each line of this file contains a TERMID followed by a tab-separated list of properties: 567\t1542\t567\t315 
    * 1542: The offset in bytes to the beginning of the line containing the inverted list for that term in term_index.txt.
    If you jump to this location and read one line, the first symbol you see should be the TERMID. 
    * 567: The total number of occurrences of the term in the entire corpus 
    * 315: The total number of documents in which the term appears 

## Term_index.txt 
 An inverted index containing the file position for each occurrence of each term in the collection. Each line contains the complete inverted list for a single term. That is, it contains a TERMID followed by a list of DOCID:POSITION values. However, in order to support more efficient compression delta encoding  is applied to the inverted list. The first DOC ID for a term and the first POSITION for a document will be stored normally. Subsequent values should be stored as the offset from the prior value. Instead of encoding an inverted list like this: 567\t1234:9\t1234:13\t1240:3\t1240:7 it is like this: 567\t1234:9\t0:4\t6:3\t0:4 
 
 
Following snippet provides more clarification of inverted index: 

![image](https://drive.google.com/uc?export=view&id=1O5M8_g0q4WsBRF5pxeLP5liSo026goLg)


## Inverted_index.py 
This file provides code for inverted index generation using hashmaps. 

## ReadIndex.txt 
This file provides statistics from inverted index. Giving inputs using command line will provide some specific stats:


Passing just **--doc DOCNAME** will list the following document information:


  $ ./read_index.py --doc clueweb12-0000tw-13-04988\
  Listing for document: clueweb12-0000tw-13-04988\
  DOCID: 1234\
  Distinct terms: 25\
  Total terms: 501\
  
  
Passing just **--term TERM** will stem the term and then list the following term information:


$ ./read_index.py --term asparagus
Listing for term: asparagus
TERMID: 567
Number of documents containing term: 315
Term frequency in corpus: 567
Inverted list offset: 1542


Passing both **--term TERM and --doc DOCNAME** will show the inverted list for the document/term:


$ ./read_index.py --term asparagus --doc clueweb12-0000tw-13-04988
Inverted list for term: asparagus
In document: clueweb12-0000tw-13-04988
TERMID: 567
DOCID: 1234
Term frequency in document: 4
Positions: 134, 155, 201, 233


## Ranker

Grade.py uses different scoring metrics like TFIDF, IDF, Okapi BM25 and Jelinek Mercer to rank the given documents for provided queries. It results In formation of small search engine where user can visualize that which documents are most relevant for specific query. 
In this project, I used 10 queries listed In topics.txt file. Using this file ranker generates resulting scores for each query with all metrics. Following table illustrates the scores for all ten queries.
  


## JELINEK MERCER SCORES

|               |     Query     |  Score           |
| ------------- | ------------- | ---------------- |
| TF Scores   | 202   | 0.0                        |
|     | 214           | 0.5341437208676446        |
|     | 216          | 0.4294449881686841         |
|     | 221        | 0.34255224066153     |
|     | 227           | 0.14966966145744265    |
|     | 230           | 0.2568956482705933       |
|     | 234           | 0.6072051329279208       |
|     | 243           | 0.30647341225591607       |
|     | 246           | 0.19030582745862082    |
|     | 250           | 0.038632952250680294       |
|     | Avg           | 0.2855323584319033    |


## TFIDF SCORES

|               |     Query     |  Score           |
| ------------- | ------------- | ---------------- |
| TF Scores   | 202   | 0.0                        |
|     | 214           | 0.43983570681388967        |
|     | 216          | 0.3584303955388199        |
|     | 221        | 0.33146057619667446        |
|     | 227           | 0.06954024467366611        |
|     | 230           | 0.18519230760824837        |
|     | 234           | 0.4274815061949275       |
|     | 243           | 0.27998906802682094       |
|     | 246           | 0.1232558916932528       |
|     | 250           | 0.02337393629631471        |
|     | Avg           | 0.22385596330426147       |

## BM25 SCORES

|               |     Query     |  Score           |
| ------------- | ------------- | ---------------- |
| TF Scores   | 202   | 0.0                        |
|     | 214           | 0.5472336230459914        |
|     | 216          | 0.4779263845212727        |
|     | 221        | 0.3738197451256454      |
|     | 227           | 0.21875689535308054        |
|     | 230           | 0.3563819001264153        |
|     | 234           | 0.6415632936438538      |
|     | 243           | 0.3201771942624003      |
|     | 246           | 0.1481816491957189      |
|     | 250           | 0.10618521546915802     |
|     | Avg           | 0.3190225890629763       |


After running all metrics correspoding file for each metric is also generated. These files rank all documents with top score documents showing on top. 
