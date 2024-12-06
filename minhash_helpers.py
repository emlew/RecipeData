import math
import random

def signature_similarity(sig1, sig2):
    size = len(sig1)
    count = 0
    for i in range(size):
        if sig1[i] == sig2[i]:
            count += 1
    return count/size

def jaccard(terms1, terms2):
    if len(terms1) == 0 and len(terms2) == 0:
        return 1.0
    s1 = set(terms1)
    s2 = set(terms2)
    return len(s1 & s2)/ len(s1 | s2)

prime_table = [53, 97, 193, 389, 769,
               1543, 3079, 6151, 12289, 24593,
               49157, 98317, 196613, 393241, 786433,
               1572869, 3145739, 6291469, 12582917, 25165843,
               50331653, 100663319, 201326611, 402653189, 805306457,
               1610612741]

def good_prime(n):
    value = round(math.log2(n) - 5)
    if value <= 0:
        return prime_table[0]
    if value >= len(prime_table):
        return prime_table[-1]
    else:
        return prime_table[value]

def generate_hash(n):
    a = random.randint(1,100)
    b = random.randint(1,100)
    p = good_prime(n)
    return lambda x: (((x*a + b) % p) % n)

common_symbols = ['.','!', '?', '-', '</br>','$', ',', ';',':','"','(',')', '{','}','[',']']

stopwords = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 
'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 
'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 
'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 
's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 
'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
 "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 
'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}
